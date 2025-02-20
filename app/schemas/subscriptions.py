# app/schemas/subscriptions.py

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

# Определяем возможные статусы подписки
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

# Базовая схема подписки
class SubscriptionBase(BaseModel):
    plan: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = SubscriptionStatus.ACTIVE

# Схема для создания подписки (связь с пользователем обязательна)
class SubscriptionCreate(SubscriptionBase):
    user_id: int

# Схема для обновления подписки
class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = None

# Схема для чтения подписки
class SubscriptionRead(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
