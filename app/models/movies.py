from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database.base import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    release_date = Column(DateTime)
    duration = Column(Integer)  # Продолжительность в минутах
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
