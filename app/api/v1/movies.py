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
    description: str = Form(None, example="A mind-bending thriller"),
    release_date: str = Form(default=str(datetime.now(timezone.utc).isoformat()),
                             example="2020-01-01T00:00:00Z"),
    duration: int = Form(..., example=70),
    rating: float = Form(..., example=8.8),
    genre: str = Form(None, example="Comedy"),
    country: str = Form(None, example="USA"),
    type_: str = Form(None, alias="type", example="movie"),
    age_rating: int = Form(0, example=18),
    required_subscription: str = Form(None, example="Premium"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Только администратор может создавать фильм
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    rd = None
    if release_date:
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
    genre: Optional[str] = Query(None, example="Comedy"),
    country: Optional[str] = Query(None, example="USA"),
    type_: Optional[str] = Query(None, alias="type", example="movie"),
    release_year_from: Optional[int] = Query(None, example=2010),
    release_year_to: Optional[int] = Query(None, example=2020),
    rating_min: Optional[float] = Query(None, example=5.0),
    rating_max: Optional[float] = Query(None, example=9.0),
    search: Optional[str] = Query(None, example="thriller"),
    sort_by: Optional[str] = Query("release_date", example="rating"),
    order: Optional[str] = Query("desc", example="asc"),
    skip: int = Query(0, example=0),
    limit: int = Query(100, example=50)
):
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
    try:
        movie = await movie_service.get_movie(db, movie_id)
        movie_data = MovieRead.from_orm(movie).dict()
        # Оставляем поле duration как число
        total_minutes = movie.duration if movie.duration is not None else 0
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes:
            formatted = f"{hours} час(а) {minutes} минут(ы)"
        else:
            formatted = f"{hours} час(а)"
        # Добавляем новое поле для отформатированной длительности
        movie_data["duration_formatted"] = formatted
        return movie_data
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie(movie_id: int, movie_in: MovieUpdate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    # Обновлять фильм может только админ
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    try:
        return await movie_service.update_movie(db, movie_id, movie_in)
    except MovieNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{movie_id}/watch")
async def watch_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    age_confirmed: Optional[str] = Cookie(None)
):
    movie = await movie_service.get_movie(db, movie_id)
    # Если фильм имеет возрастное ограничение и пользователь не подтвердил возраст
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
