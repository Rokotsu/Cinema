# app/schemas/users.py

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

# Определяем допустимые роли
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Базовая схема для пользователя
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Схема для создания пользователя (при регистрации)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Схема для обновления пользователя (например, изменение email или username)
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = Field(None, min_length=8)

# Схема для чтения пользователя (возвращается клиенту, не содержит пароль)
class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
