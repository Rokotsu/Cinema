# File: app/api/v1/movies.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.movies import MovieCreate, MovieRead, MovieUpdate
from app.services.movies_service import MovieService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import MovieNotFoundException
from app.models.users import User
from app.core.security import get_current_user
from app.services.subscriptions_service import SubscriptionService

router = APIRouter(prefix="/movies", tags=["movies"])
movie_service = MovieService()

@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
async def create_movie(movie_in: MovieCreate, db: AsyncSession = Depends(get_db_session)):
    return await movie_service.create_movie(db, movie_in)

@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await movie_service.get_movie(db, movie_id)
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie(movie_id: int, movie_in: MovieUpdate, db: AsyncSession = Depends(get_db_session)):
    try:
        return await movie_service.update_movie(db, movie_id, movie_in)
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/", response_model=List[MovieRead])
async def list_movies(db: AsyncSession = Depends(get_db_session)):
    return await movie_service.list_movies(db)

@router.get("/{movie_id}/watch")
async def watch_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    movie = await movie_service.get_movie(db, movie_id)
    # Если фильм бесплатный (поле required_subscription не заполнено) – разрешаем просмотр
    if not movie.required_subscription:
        return {"movie_id": movie.id, "stream_url": f"http://example.com/stream/{movie.id}"}

    # Если фильм требует подписки, проверяем наличие активной (оплаченной) подписки
    subscription_service = SubscriptionService()
    subscription = await subscription_service.get_active_subscription(db, current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подписка не оформлена или не оплачена. Пожалуйста, оформите и оплатите подписку перед просмотром."
        )
    # Сравниваем планы подписки без учета регистра
    if subscription.plan.lower() != movie.required_subscription.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ваша подписка ({subscription.plan}) не дает доступа к этому фильму. Для просмотра требуется подписка {movie.required_subscription}."
        )
    return {"movie_id": movie.id, "stream_url": f"http://example.com/stream/{movie.id}"}
