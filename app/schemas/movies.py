# app/schemas/movies.py

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

# Схема для создания фильма (требуется, как минимум, заголовок)
class MovieCreate(MovieBase):
    title: str

# Схема для обновления данных фильма
class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    rating: Optional[float] = None

# Схема для чтения данных о фильме
class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
