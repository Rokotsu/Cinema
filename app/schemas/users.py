# File: app/schemas/users.py
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class LoginForm(BaseModel):
    username: str
    password: str

    class Config:
        extra = "forbid"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = Field(None, min_length=8)

class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

from typing import Optional
from app.schemas.subscriptions import SubscriptionRead

class UserWithSubscription(BaseModel):
    user: UserRead
    subscription: Optional[SubscriptionRead] = None
    remaining_days: int
    message: str

    class Config:
        orm_mode = True
        from_attributes = True
