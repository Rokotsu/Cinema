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
    genre: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None       # "movie" или "series"
    age_rating: Optional[int] = None
    required_subscription: Optional[str] = None

class MovieCreate(MovieBase):
    title: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    duration: Optional[int] = None
    rating: Optional[float] = None
    genre: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    age_rating: Optional[int] = None
    required_subscription: Optional[str] = None

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
