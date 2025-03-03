# File: app/models/movies.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database.base import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    release_date = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer)  # продолжительность фильма в минутах
    rating = Column(Float, default=0.0)
    genre = Column(String(50), nullable=True)       # жанр фильма, например "Comedy", "Horror"
    country = Column(String(50), nullable=True)       # страна производства
    type = Column(String(20), nullable=True)          # "movie" или "series"
    age_rating = Column(Integer, nullable=True)       # минимальный возраст (например, 18)
    required_subscription = Column(String(50), nullable=True)  # если указан, для просмотра требуется подписка
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
