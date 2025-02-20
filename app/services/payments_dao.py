# app/services/payments_service.py

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.payments_dao import PaymentDAO
from app.schemas.payments import PaymentCreate, PaymentUpdate
from app.models.payments import Payment
from app.exceptions.custom_exceptions import PaymentNotFoundException, PaymentProcessingException

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, payment_dao: Optional[PaymentDAO] = None):
        self.payment_dao = payment_dao or PaymentDAO()

    async def create_payment(self, db: AsyncSession, payment_in: PaymentCreate) -> Payment:
        payment_data = payment_in.dict()
        payment = await self.payment_dao.create(db, payment_data)
        logger.info(f"Создан платёж с id {payment.id} для пользователя {payment.user_id}")

        # Пример интеграции с платежным шлюзом:
        # try:
        #     gateway_response = await initiate_payment(payment_data)
        #     if not gateway_response.success:
        #         raise PaymentProcessingException()
        #     payment = await self.payment_dao.update(db, payment, {"status": gateway_response.status})
        # except Exception as e:
        #     logger.error(f"Ошибка при обработке платежа: {str(e)}")
        #     raise PaymentProcessingException()

        return payment

    async def update_payment(self, db: AsyncSession, payment_id: int, payment_in: PaymentUpdate) -> Payment:
        payment = await self.payment_dao.get_by_id(db, payment_id)
        if not payment:
            logger.error(f"Платёж с id {payment_id} не найден")
            raise PaymentNotFoundException()
        payment = await self.payment_dao.update(db, payment, payment_in.dict(exclude_unset=True))
        logger.info(f"Платёж с id {payment.id} обновлён")
        return payment

    async def get_payment(self, db: AsyncSession, payment_id: int) -> Optional[Payment]:
        payment = await self.payment_dao.get_by_id(db, payment_id)
        if not payment:
            logger.warning(f"Платёж с id {payment_id} не найден")
            raise PaymentNotFoundException()
        return payment

    async def list_payments(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Payment]:
        payments = await self.payment_dao.list(db, skip, limit)
        logger.info(f"Получено {len(payments)} платежей")
        return payments
