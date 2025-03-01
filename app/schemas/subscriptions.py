# File: app/schemas/subscriptions.py
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class SubscriptionStatus(str, Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class SubscriptionBase(BaseModel):
    plan: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = SubscriptionStatus.pending

class SubscriptionCreate(SubscriptionBase):
    class Config:
        extra = "forbid"

class SubscriptionRead(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True  # Добавлено для поддержки from_orm

class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SubscriptionStatus] = None

    class Config:
        extra = "forbid"
