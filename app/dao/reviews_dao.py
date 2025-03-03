# File: app/dao/reviews_dao.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reviews import Review
from app.dao.base import BaseDAO

class ReviewDAO(BaseDAO[Review]):
    def __init__(self):
        super().__init__(Review)
