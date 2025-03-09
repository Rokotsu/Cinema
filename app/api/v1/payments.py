from fastapi import APIRouter, Request, Depends, Form
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db_session
from app.core.config import settings
from app.services.payments_dao import PaymentService
from app.services.subscriptions_service import SubscriptionService
from app.schemas.payments import PaymentCreate
from app.models.payments import PaymentStatus
from app.schemas.subscriptions import SubscriptionStatus as SubStatus
from app.exceptions.custom_exceptions import (
    SubscriptionNotFoundException,
    StripeWebhookException
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Обработчик вебхука Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise StripeWebhookException(str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        subscription_id_str = session["metadata"].get("subscription_id", "").strip()
        payment_service = PaymentService()
        await payment_service.update_payment(db, int(order_id), {"status": PaymentStatus.COMPLETED})
        payment = await payment_service.get_payment(db, int(order_id))
        if subscription_id_str:
            subscription_service = SubscriptionService()
            try:
                subscription = await subscription_service.get_subscription(db, int(subscription_id_str))
                await subscription_service.update_subscription(db, subscription.id, {"status": SubStatus.active})
            except SubscriptionNotFoundException:
                pass
    return {"status": "success"}


@router.post("/initiate", response_model=dict)
async def initiate_payment_endpoint(
        amount: float = Form(..., title="Amount", example=1000.0),
        currency: str = Form(..., title="Currency", example="RUB"),
        payment_method: str = Form(..., title="Payment Method", example="card"),
        user_id: int = Form(..., title="User ID", example=1),
        subscription_id: int = Form(..., title="Subscription ID", example=123),
        db: AsyncSession = Depends(get_db_session)
):
    """
    Инициализирует платеж через Stripe.
    """
    payment_in = PaymentCreate(
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        user_id=user_id,
        subscription_id=subscription_id
    )
    payment_service = PaymentService()
    result = await payment_service.initiate_payment(db, payment_in)
    return result
