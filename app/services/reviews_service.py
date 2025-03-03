# File: app/services/reviews_service.py
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.reviews_dao import ReviewDAO
from app.schemas.reviews import ReviewCreate, ReviewUpdate
from app.models.reviews import Review
from app.exceptions.custom_exceptions import ReviewNotFoundException

logger = logging.getLogger(__name__)

class ReviewService:
    def __init__(self, review_dao: Optional[ReviewDAO] = None):
        self.review_dao = review_dao or ReviewDAO()

    async def create_review(self, db: AsyncSession, review_in: ReviewCreate) -> Review:
        review = await self.review_dao.create(db, review_in.dict())
        logger.info(f"Создан отзыв с id {review.id} для фильма {review.movie_id}")
        return review

    async def list_reviews_for_movie(self, db: AsyncSession, movie_id: int) -> List[Review]:
        from sqlalchemy import select
        stmt = select(Review).where(Review.movie_id == movie_id, Review.is_deleted == False)
        result = await db.execute(stmt)
        reviews = result.scalars().all()
        return reviews

    async def delete_review(self, db: AsyncSession, review_id: int) -> Review:
        review = await self.review_dao.get_by_id(db, review_id)
        if not review:
            raise ReviewNotFoundException()
        # Вместо физического удаления, помечаем как удалённый
        review = await self.review_dao.update(db, review, {"is_deleted": True})
        return review

    async def update_review(self, db: AsyncSession, review_id: int, review_in: ReviewUpdate) -> Review:
        review = await self.review_dao.get_by_id(db, review_id)
        if not review:
            raise ReviewNotFoundException()
        review = await self.review_dao.update(db, review, review_in.dict(exclude_unset=True))
        return review
