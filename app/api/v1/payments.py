from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db_session
from app.core.config import settings
from app.services.payments_dao import PaymentService
from app.services.subscriptions_service import SubscriptionService

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

    # Обработка события успешного платежа
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        payment_service = PaymentService()
        # Обновляем статус платежа на "completed"
        await payment_service.update_payment(db, int(order_id), {"status": "completed"})
        # Если платеж связан с подпиской, обновляем статус подписки на "active"
        payment = await payment_service.get_payment(db, int(order_id))
        if payment.subscription_id:
            subscription_service = SubscriptionService()
            await subscription_service.update_subscription(db, payment.subscription_id, {"status": "active"})
    return {"status": "success"}
