from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.subscriptions import SubscriptionCreateInput, SubscriptionRead, SubscriptionUpdate
from app.services.subscriptions_service import SubscriptionService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import SubscriptionNotFoundException
from app.core.security import get_current_user
from app.models.users import User
from app.models.subscriptions import SubscriptionStatus  # импортируем enum из модели

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
subscription_service = SubscriptionService()


@router.post("/purchase", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
async def purchase_subscription(
    sub_in: SubscriptionCreateInput,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    sub_data = sub_in.model_dump()  # или sub_in.dict() если используете Pydantic <2.0
    sub_data["user_id"] = current_user.id
    # Вместо строки "pending" передаем объект enum:
    sub_data["status"] = SubscriptionStatus.PENDING
    subscription = await subscription_service.create_subscription(db, sub_data)
    return subscription


