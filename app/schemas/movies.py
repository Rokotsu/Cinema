# File: app/schemas/movies.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    rating: Optional[float] = 0.0
    required_subscription: Optional[str] = None  # NEW: указывает необходимую подписку для просмотра

class MovieCreate(MovieBase):
    title: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    required_subscription: Optional[str] = None  # NEW

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
