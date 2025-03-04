# File: app/api/v1/movies.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
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
async def create_movie(
    title: str = Form(..., example="Inception"),
    description: Optional[str] = Form(None, example="A mind-bending thriller"),
    release_date: str = Form(default=str(datetime.now(timezone.utc).isoformat()),
                             example="2020-01-01T00:00:00Z"),
    duration: int = Form(..., example=148),
    rating: float = Form(..., example=8.8),
    genre: Optional[str] = Form(None, example="Comedy"),
    country: Optional[str] = Form(None, example="USA"),
    type_: Optional[str] = Form(None, example="movie"),
    age_rating: Optional[int] = Form(0, example=18),
    required_subscription: Optional[str] = Form(None, example="Premium"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создает новый фильм.

    Критически важные поля: title, duration и rating.
    Остальные поля являются опциональными.
    Только администратор имеет доступ к созданию фильма.
    """
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    try:
        rd = datetime.fromisoformat(release_date.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Неверный формат release_date. Ожидается ISO формат, например: 2020-01-01T00:00:00Z"
        )
    movie_in = MovieCreate(
        title=title,
        description=description,
        release_date=rd,
        duration=duration,
        rating=rating,
        genre=genre,
        country=country,
        type=type_,
        age_rating=age_rating,
        required_subscription=required_subscription
    )
    return await movie_service.create_movie(db, movie_in)

@router.get("/", response_model=List[MovieRead])
async def list_movies(
    db: AsyncSession = Depends(get_db_session),
    search: str = Query(..., alias="title", description="Title for movie search", example="thriller"),
    genre: Optional[str] = Query(None, example="Comedy"),
    country: Optional[str] = Query(None, example="USA"),
    type_: Optional[str] = Query(None, example="movie"),
    release_year_from: Optional[int] = Query(None, alias="release_year_from", example=2010),
    release_year_to: Optional[int] = Query(None, alias="release_year_to", example=2020),
    rating_min: Optional[float] = Query(None, alias="rating_min", example=5.0),
    rating_max: Optional[float] = Query(None, alias="rating_max", example=9.0),
    sort_by: Optional[str] = Query("release_date", alias="sort_by", example="rating"),
    order: Optional[str] = Query("desc", alias="order", example="asc"),
    skip: int = Query(0, alias="skip", example=0),
    limit: int = Query(100, alias="limit", example=50)
):
    """
    Возвращает список фильмов по заданным фильтрам.

    Обязательное поле: title для поиска по названию фильма.
    Остальные параметры фильтрации являются опциональными.
    """
    return await movie_service.list_movies(
        db,
        genre,
        country,
        type_,
        release_year_from,
        release_year_to,
        rating_min,
        rating_max,
        search,
        sort_by,
        order,
        skip,
        limit
    )

@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Возвращает подробную информацию о фильме по его идентификатору.
    """
    try:
        movie = await movie_service.get_movie(db, movie_id)
        movie_data = MovieRead.from_orm(movie).dict()
        total_minutes = movie.duration if movie.duration is not None else 0
        hours = total_minutes // 60
        minutes = total_minutes % 60
        formatted = f"{hours} hr {minutes} min" if minutes else f"{hours} hr"
        movie_data["duration_formatted"] = formatted
        return movie_data
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie(
    movie_id: int,
    title: Optional[str] = Form(None, example="Updated Movie Title"),
    description: Optional[str] = Form(None, example="Updated description"),
    release_date: Optional[str] = Form(None, example="2020-01-01T00:00:00Z"),
    duration: Optional[int] = Form(None, example=120),
    rating: Optional[float] = Form(None, example=8.0),
    genre: Optional[str] = Form(None, example="Comedy"),
    country: Optional[str] = Form(None, example="USA"),
    type_: Optional[str] = Form(None, example="movie"),
    age_rating: Optional[int] = Form(None, example=16),
    required_subscription: Optional[str] = Form(None, example="Premium"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновляет данные фильма по его идентификатору.
    Только администратор имеет право обновлять информацию о фильме.
    """
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if release_date is not None:
        try:
            update_data["release_date"] = datetime.fromisoformat(release_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=422, detail="Неверный формат release_date. Ожидается ISO формат.")
    if duration is not None:
        update_data["duration"] = duration
    if rating is not None:
        update_data["rating"] = rating
    if genre is not None:
        update_data["genre"] = genre
    if country is not None:
        update_data["country"] = country
    if type_ is not None:
        update_data["type"] = type_
    if age_rating is not None:
        update_data["age_rating"] = age_rating
    if required_subscription is not None:
        update_data["required_subscription"] = required_subscription
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    movie_update = MovieUpdate(**update_data)
    try:
        return await movie_service.update_movie(db, movie_id, movie_update)
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{movie_id}/watch")
async def watch_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    age_confirmed: Optional[str] = Cookie(None)
):
    """
    Предоставляет доступ к просмотру фильма.
    Если фильм имеет возрастное ограничение, проверяется подтверждение возраста.
    Также проверяется наличие активной подписки, если фильм требует подписку.
    """
    movie = await movie_service.get_movie(db, movie_id)
    if movie.age_rating and movie.age_rating >= 18:
        if age_confirmed != "true":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Для просмотра данного фильма необходимо подтвердить, что вам 18+."
            )
    if not movie.required_subscription:
        return {"movie_id": movie.id, "stream_url": f"http://example.com/stream/{movie.id}"}
    subscription_service = SubscriptionService()
    subscription = await subscription_service.get_active_subscription(db, current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подписка не оформлена или не оплачена. Пожалуйста, оформите и оплатите подписку перед просмотром."
        )
    if subscription.plan.lower() != movie.required_subscription.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ваша подписка ({subscription.plan}) не дает доступа к этому фильму. Для просмотра требуется подписка {movie.required_subscription}."
        )
    return {"movie_id": movie.id, "stream_url": f"http://example.com/stream/{movie.id}"}
