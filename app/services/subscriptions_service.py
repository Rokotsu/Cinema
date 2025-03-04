# File: app/services/subscriptions_service.py
import logging
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.subscriptions_dao import SubscriptionDAO
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate
from app.models.subscriptions import Subscription
from app.exceptions.custom_exceptions import SubscriptionNotFoundException

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, subscription_dao: Optional[SubscriptionDAO] = None):
        self.subscription_dao = subscription_dao or SubscriptionDAO()

    async def create_subscription(self, db: AsyncSession, sub_data: dict) -> Subscription:
        if not sub_data.get("start_date"):
            sub_data["start_date"] = datetime.now(timezone.utc)
        subscription = await self.subscription_dao.create(db, sub_data)
        logger.info(f"Создана подписка с id {subscription.id} для пользователя {subscription.user_id}")
        return subscription

    async def update_subscription(self, db: AsyncSession, sub_id: int, sub_in) -> Subscription:
        subscription = await self.subscription_dao.get_by_id(db, sub_id)
        if not subscription:
            logger.error(f"Подписка с id {sub_id} не найдена")
            raise SubscriptionNotFoundException()
        if isinstance(sub_in, dict):
            updated_data = sub_in
        else:
            updated_data = sub_in.dict(exclude_unset=True)
        subscription = await self.subscription_dao.update(db, subscription, updated_data)
        logger.info(f"Подписка с id {subscription.id} обновлена")
        return subscription

    async def get_subscription(self, db: AsyncSession, sub_id: int) -> Subscription:
        subscription = await self.subscription_dao.get_by_id(db, sub_id)
        if not subscription:
            logger.warning(f"Подписка с id {sub_id} не найдена")
            raise SubscriptionNotFoundException()
        return subscription

    async def list_subscriptions(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Subscription]:
        subscriptions = await self.subscription_dao.list(db, skip, limit)
        logger.info(f"Получено {len(subscriptions)} подписок")
        return subscriptions

    async def get_active_subscription(self, db: AsyncSession, user_id: int):
        subscriptions = await self.subscription_dao.list(db, skip=0, limit=100)
        for sub in subscriptions:
            if sub.user_id == user_id and sub.status.value.lower() == "active":
                return sub
        return None

    async def get_subscription_by_plan(self, db: AsyncSession, user_id: int, plan: str) -> Optional[Subscription]:
        subscriptions = await self.subscription_dao.list(db, skip=0, limit=1000)
        for sub in subscriptions:
            if sub.user_id == user_id and sub.plan.lower() == plan.lower():
                return sub
        return None
