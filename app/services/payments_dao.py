# File: app/services/payments_dao.py
import stripe
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.payments_dao import PaymentDAO
from app.schemas.payments import PaymentCreate
from app.models.payments import Payment, PaymentStatus
from app.exceptions.custom_exceptions import PaymentNotFoundException
from app.core.config import settings

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, payment_dao: PaymentDAO = None):
        self.payment_dao = payment_dao or PaymentDAO()

    async def create_payment(self, db: AsyncSession, payment_in: PaymentCreate) -> Payment:
        payment_data = payment_in.dict()
        # Извлекаем subscription_plan, чтобы его не передавать в модель Payment
        subscription_plan = payment_data.pop("subscription_plan", None)
        payment = await self.payment_dao.create(db, payment_data)
        logger.info(f"Создан платёж с id {payment.id} для пользователя {payment.user_id}")
        return payment

    async def update_payment(self, db: AsyncSession, payment_id: int, update_data: dict) -> Payment:
        payment = await self.payment_dao.get_by_id(db, payment_id)
        if not payment:
            raise PaymentNotFoundException()
        payment = await self.payment_dao.update(db, payment, update_data)
        logger.info(f"Обновлён платёж с id {payment.id}")
        return payment

    async def get_payment(self, db: AsyncSession, payment_id: int) -> Payment:
        payment = await self.payment_dao.get_by_id(db, payment_id)
        if not payment:
            raise PaymentNotFoundException()
        return payment

    async def initiate_payment(self, db: AsyncSession, payment_in: PaymentCreate) -> dict:
        payment = await self.create_payment(db, payment_in)
        order_id = str(payment.id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Оплата подписки {payment_in.subscription_plan or ''}".strip()},
                        "unit_amount": int(payment.amount * 100)
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:8000/cancel",
                metadata={"order_id": order_id, "subscription_plan": payment_in.subscription_plan or ""}
            )
            logger.info(f"Создан Stripe Checkout Session для платежа {payment.id}")
            return {"payment_id": payment.id, "checkout_url": checkout_session.url}
        except Exception as e:
            raise Exception(f"Ошибка Stripe: {str(e)}")
