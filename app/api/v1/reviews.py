# File: app/api/v1/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.reviews import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.reviews_service import ReviewService
from app.database.dependencies import get_db_session
from app.core.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/reviews", tags=["reviews"])
review_service = ReviewService()

@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    movie_id: int = Form(..., example=1),
    rating: int = Form(..., example=8),
    comment: Optional[str] = Form(None, example="Great movie!"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создает новый отзыв для фильма.
    Критически важные поля: movie_id и rating.
    Комментарий является опциональным.
    """
    review_in = ReviewCreate(movie_id=movie_id, user_id=current_user.id, rating=rating, comment=comment)
    review = await review_service.create_review(db, review_in)
    return review

@router.get("/movie/{movie_id}", response_model=List[ReviewRead])
async def get_reviews_for_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Возвращает список отзывов для фильма по его идентификатору.
    """
    reviews = await review_service.list_reviews_for_movie(db, movie_id)
    return reviews

@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет отзыв по его идентификатору.
    Отзыв может быть удалён только администратором.
    """
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    review = await review_service.delete_review(db, review_id)
    return {"message": "Отзыв удалён", "review_id": review.id}

@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    rating: Optional[int] = Form(None, example=9),
    comment: Optional[str] = Form(None, example="Updated review"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновляет отзыв по его идентификатору.
    Поля rating и comment являются опциональными.
    Обновление может быть выполнено только автором отзыва или администратором.
    """
    update_data = {}
    if rating is not None:
        update_data["rating"] = rating
    if comment is not None:
        update_data["comment"] = comment
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    review_update = ReviewUpdate(**update_data)
    review = await review_service.update_review(db, review_id, review_update)
    if review.user_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    return review
