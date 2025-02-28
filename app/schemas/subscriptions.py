# app/schemas/subscriptions.py

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class SubscriptionStatus(str, Enum):
    pending = "pending"      # добавлено
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class SubscriptionBase(BaseModel):
    plan: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = SubscriptionStatus.pending

# Схема для создания подписки – без поля user_id
class SubscriptionCreateInput(SubscriptionBase):
    class Config:
        extra = "forbid"

# Схема для чтения подписки – включает поле user_id
class SubscriptionRead(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Схема для обновления подписки (без поля user_id)
class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = None

    class Config:
        extra = "forbid"
