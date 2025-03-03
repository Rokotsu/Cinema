# File: app/api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
    SubscriptionStatus
)
from app.services.subscriptions_service import SubscriptionService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import SubscriptionNotFoundException
from app.core.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
subscription_service = SubscriptionService()

@router.post("/purchase", status_code=status.HTTP_200_OK)
async def purchase_subscription(
    plan: str = Form(..., example="Premium"),
    start_date: str = Form(default=str(datetime.now(timezone.utc).isoformat()),
                           example="2025-03-02T00:00:00Z"),
    end_date: str = Form(default=str(datetime.now(timezone.utc).isoformat()),
                         example="2025-04-02T00:00:00Z"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    user_subscriptions = await subscription_service.list_subscriptions(db, skip=0, limit=100)
    for sub in user_subscriptions:
        if sub.user_id == current_user.id and sub.status.value.lower() in ["pending", "active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"У вас уже есть подписка: {sub.plan} со статусом {sub.status.value}. Завершите оплату, чтобы продолжить."
            )
    sd = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    ed = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    sub_in = SubscriptionCreate(
        plan=plan,
        start_date=sd,
        end_date=ed
    )
    sub_data = sub_in.model_dump()
    sub_data["user_id"] = current_user.id
    sub_data["status"] = SubscriptionStatus.pending
    new_subscription = await subscription_service.create_subscription(db, sub_data)
    return {
        "message": "Подписка оформлена. Пожалуйста, перейдите к оплате.",
        "subscription": SubscriptionRead.from_orm(new_subscription)
    }

@router.get("/me", response_model=SubscriptionRead)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    subscriptions = await subscription_service.list_subscriptions(db, skip=0, limit=100)
    user_sub = next((sub for sub in subscriptions if sub.user_id == current_user.id and sub.status.value.lower() in ["pending", "active"]), None)
    if not user_sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Подписка не найдена.")
    return SubscriptionRead.from_orm(user_sub)
