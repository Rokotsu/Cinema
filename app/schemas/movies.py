from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Базовая схема для фильма/сериала
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None  # Продолжительность в минутах
    rating: Optional[float] = 0.0
    subscription_required: bool = False
    required_plan: Optional[str] = None  # <--- Добавляем поле для уровня подписки

class MovieCreate(MovieBase):
    title: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    subscription_required: Optional[bool] = None
    required_plan: Optional[str] = None  # <--- При обновлении тоже можно менять план

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
