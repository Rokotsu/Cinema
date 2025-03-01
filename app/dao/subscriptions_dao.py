# File: app/dao/subscriptions_dao.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscriptions import Subscription
from app.dao.base import BaseDAO

class SubscriptionDAO(BaseDAO[Subscription]):
    def __init__(self):
        super().__init__(Subscription)
