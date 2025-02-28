from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from app.database.base import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    release_date = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer)  # Продолжительность в минутах
    rating = Column(Float, default=0.0)
    subscription_required = Column(Boolean, default=False, nullable=False)

    # Новое поле для указания, какой план подписки требуется. Например, "Basic", "Premium" и т.п.
    required_plan = Column(String(50), nullable=True, default=None)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
