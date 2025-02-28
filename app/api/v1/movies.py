# app/api/v1/movies.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.movies import MovieCreate, MovieRead, MovieUpdate
from app.services.movies_service import MovieService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import MovieNotFoundException

# Новые импорты для проверки подписки
from app.core.security import get_current_user
from app.models.users import User
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

# Новый эндпоинт для просмотра фильма
@router.get("/{movie_id}/watch")
async def watch_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Получаем фильм
    movie = await movie_service.get_movie(db, movie_id)

    # Если фильм требует подписку – проверяем наличие активной подписки у пользователя
    if movie.subscription_required:
        # Если в фильме указан конкретный план, проверяем, есть ли у пользователя активная подписка именно с таким планом
        if movie.required_plan:
            subscription_service = SubscriptionService()
            active_subscription = await subscription_service.get_active_subscription_for_plan(
                db, current_user.id, movie.required_plan
            )
            if not active_subscription:
                # Нет подписки с нужным планом
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=(
                        f"Для просмотра этого фильма требуется план подписки '{movie.required_plan}'. "
                        f"Пожалуйста, оформите нужную подписку."
                    )
                )
        else:
            # Если subscription_required = True, но required_plan = None,
            # решите логику сами: либо не давать смотреть, либо считать, что
            # достаточно любой активной подписки:
            subscription_service = SubscriptionService()
            active_subscription = await subscription_service.get_active_subscription(db, current_user.id)
            if not active_subscription:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Для просмотра данного фильма требуется подписка (план не указан)."
                )

    # Если дошли сюда, значит либо фильм не требует подписки, либо подписка нужного плана есть
    return {"streaming_url": f"http://streaming-service/movies/{movie_id}"}

@router.get("/", response_model=List[MovieRead])
async def list_all_movies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Эндпоинт возвращает список всех фильмов (платных и бесплатных)
    с поддержкой пагинации.
    """
    movies = await movie_service.list_movies(db, skip, limit)
    return movies
