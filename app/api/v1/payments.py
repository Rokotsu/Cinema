# File: app/api/v1/payments.py
from fastapi import APIRouter, Request, HTTPException, Depends, Form
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db_session
from app.core.config import settings
from app.services.payments_dao import PaymentService
from app.services.subscriptions_service import SubscriptionService
from app.schemas.payments import PaymentCreate
from app.models.payments import PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректное тело запроса")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Некорректная подпись")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        payment_service = PaymentService()
        await payment_service.update_payment(db, int(order_id), {"status": PaymentStatus.COMPLETED})
        payment = await payment_service.get_payment(db, int(order_id))
        if payment.subscription_id:
            subscription_service = SubscriptionService()
            await subscription_service.update_subscription(db, payment.subscription_id, {"status": "ACTIVE"})
    return {"status": "success"}

@router.post("/initiate", response_model=dict)
async def initiate_payment_endpoint(
    amount: float = Form(..., example=1000.0),
    currency: str = Form(..., example="RUB"),
    payment_method: str = Form(..., example="card"),
    user_id: int = Form(..., example=1),
    subscription_id: int = Form(None, example=3),
    db: AsyncSession = Depends(get_db_session)
):
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
