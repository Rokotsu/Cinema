# File: app/api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate, SubscriptionStatus
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
    start_date: str = Form(default=str(datetime.now(timezone.utc).isoformat()), example="2025-03-02T00:00:00Z"),
    end_date: str = Form(default="", example=""),  # если пусто, рассчитываем автоматически
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Оформляет подписку для текущего пользователя.

    Если у пользователя уже есть активная или ожидающая оплата подписка, возвращается ошибка.
    Если end_date не указана, рассчитывается автоматически (30 дней от start_date).
    """
    user_subscriptions = await subscription_service.list_subscriptions(db, skip=0, limit=100)
    for sub in user_subscriptions:
        if sub.user_id == current_user.id and sub.status.value.lower() in ["pending", "active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"У вас уже есть подписка: {sub.plan} со статусом {sub.status.value}. Завершите оплату, чтобы продолжить."
            )
    try:
        sd = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=422, detail="Неверный формат start_date. Ожидается ISO формат.")
    if end_date.strip() == "":
        ed = sd + timedelta(days=30)
    else:
        try:
            ed = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=422, detail="Неверный формат end_date. Ожидается ISO формат.")
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

@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(subscription_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает информацию о подписке по её идентификатору.
    """
    try:
        return await subscription_service.get_subscription(db, subscription_id)
    except SubscriptionNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription(
    subscription_id: int,
    plan: Optional[str] = Form(None, example="Updated Plan"),
    start_date: Optional[str] = Form(None, example="2025-03-02T00:00:00Z"),
    end_date: Optional[str] = Form(None, example="2025-04-02T00:00:00Z"),
    status: Optional[str] = Form(None, example="active"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Обновляет данные подписки по её идентификатору.
    """
    update_data = {}
    if plan is not None:
        update_data["plan"] = plan
    if start_date is not None:
        try:
            update_data["start_date"] = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=422, detail="Неверный формат start_date. Ожидается ISO формат.")
    if end_date is not None:
        try:
            update_data["end_date"] = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=422, detail="Неверный формат end_date. Ожидается ISO формат.")
    if status is not None:
        update_data["status"] = status
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    subscription_update = SubscriptionUpdate(**update_data)
    try:
        return await subscription_service.update_subscription(db, subscription_id, subscription_update)
    except SubscriptionNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
