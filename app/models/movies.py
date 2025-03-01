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
    duration = Column(Integer)
    rating = Column(Float, default=0.0)
    required_subscription = Column(String(50), nullable=True)  # NEW: указывает, какая подписка нужна для просмотра (если не указано – фильм бесплатный)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
