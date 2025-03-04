# File: app/schemas/payments.py
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentBase(BaseModel):
    amount: float = Field(..., title="Amount")
    currency: Optional[str] = Field("RUB", title="Currency")
    payment_method: Optional[str] = Field(None, title="Payment Method")

class PaymentCreate(PaymentBase):
    user_id: int = Field(..., title="User ID")
    subscription_id: int = Field(..., title="Subscription ID")

class PaymentUpdate(BaseModel):
    amount: Optional[float] = Field(None, title="Amount")
    currency: Optional[str] = Field(None, title="Currency")
    payment_method: Optional[str] = Field(None, title="Payment Method")
    status: Optional[PaymentStatus] = Field(None, title="Status")
    transaction_id: Optional[str] = Field(None, title="Transaction ID")

class PaymentRead(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatus
    transaction_id: Optional[str] = Field(None, title="Transaction ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
