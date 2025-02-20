# app/dao/payments_dao.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payments import Payment
from app.dao.base import BaseDAO

class PaymentDAO(BaseDAO[Payment]):
    def __init__(self):
        super().__init__(Payment)
