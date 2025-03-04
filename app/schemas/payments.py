# File: app/schemas/payments.py
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentBase(BaseModel):
    amount: float
    currency: Optional[str] = "RUB"
    payment_method: Optional[str] = None

class PaymentCreate(PaymentBase):
    user_id: int
    subscription_plan: Optional[str] = None  # Новое поле: план подписки по названию

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    payment_method: Optional[str] = None
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None

class PaymentRead(PaymentBase):
    id: int
    user_id: int
    # Убираем поле subscription_id, так как теперь работаем по плану подписки
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
