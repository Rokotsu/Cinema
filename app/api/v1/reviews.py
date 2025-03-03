# File: app/api/v1/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
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
    comment: str = Form(None, example="Отличный фильм!"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    review_in = ReviewCreate(movie_id=movie_id, user_id=current_user.id, rating=rating, comment=comment)
    review = await review_service.create_review(db, review_in)
    return review

@router.get("/movie/{movie_id}", response_model=list[ReviewRead])
async def get_reviews_for_movie(movie_id: int, db: AsyncSession = Depends(get_db_session)):
    reviews = await review_service.list_reviews_for_movie(db, movie_id)
    return reviews

@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    # Удалять отзыв может только админ
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    review = await review_service.delete_review(db, review_id)
    return {"message": "Отзыв удалён", "review_id": review.id}

@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    rating: int = Form(None, example=9),
    comment: str = Form(None, example="Обновлённый отзыв"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Обновлять отзыв может только его автор или админ
    review_in = ReviewUpdate(rating=rating, comment=comment)
    review = await review_service.update_review(db, review_id, review_in)
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    return review
