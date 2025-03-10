# File: app/services/movies_service.py
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timezone
from app.dao.movies_dao import MovieDAO
from app.schemas.movies import MovieCreate, MovieUpdate
from app.models.movies import Movie
from app.exceptions.custom_exceptions import MovieNotFoundException

logger = logging.getLogger(__name__)

class MovieService:
    def __init__(self, movie_dao: Optional[MovieDAO] = None):
        self.movie_dao = movie_dao or MovieDAO()

    async def create_movie(self, db: AsyncSession, movie_in: MovieCreate) -> Movie:
        movie = await self.movie_dao.create(db, movie_in.dict())
        logger.info(f"Создан фильм с id {movie.id}")
        return movie

    async def update_movie(self, db: AsyncSession, movie_id: int, movie_in: MovieUpdate) -> Movie:
        movie = await self.movie_dao.get_by_id(db, movie_id)
        if not movie:
            logger.error(f"Фильм с id {movie_id} не найден для обновления")
            raise MovieNotFoundException()
        updated_data = movie_in.dict(exclude_unset=True)
        movie = await self.movie_dao.update(db, movie, updated_data)
        logger.info(f"Фильм с id {movie.id} обновлён")
        return movie

    async def get_movie(self, db: AsyncSession, movie_id: int) -> Movie:
        movie = await self.movie_dao.get_by_id(db, movie_id)
        if not movie:
            logger.warning(f"Фильм с id {movie_id} не найден")
            raise MovieNotFoundException()
        return movie

    async def list_movies(
        self,
        db: AsyncSession,
        genre: Optional[str] = None,
        country: Optional[str] = None,
        type_: Optional[str] = None,
        release_year_from: Optional[int] = None,
        release_year_to: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = "release_date",  # по умолчанию сортировка по дате выпуска
        order: Optional[str] = "desc",            # по умолчанию — от новых к старым
        skip: int = 0,
        limit: int = 100
    ) -> List[Movie]:
        stmt = select(Movie)
        conditions = []
        if genre:
            conditions.append(Movie.genre.ilike(f"%{genre}%"))
        if country:
            conditions.append(Movie.country.ilike(f"%{country}%"))
        if type_:
            conditions.append(Movie.type.ilike(f"%{type_}%"))
        if release_year_from:
            conditions.append(Movie.release_date >= datetime(release_year_from, 1, 1, tzinfo=timezone.utc))
        if release_year_to:
            conditions.append(Movie.release_date <= datetime(release_year_to, 12, 31, tzinfo=timezone.utc))
        if rating_min is not None:
            conditions.append(Movie.rating >= rating_min)
        if rating_max is not None:
            conditions.append(Movie.rating <= rating_max)
        if search:
            conditions.append(or_(
                Movie.title.ilike(f"%{search}%"),
                Movie.description.ilike(f"%{search}%")
            ))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        # Сортировка: разрешаем сортировать по rating, release_date, title
        allowed_sort_fields = {
            "rating": Movie.rating,
            "release_date": Movie.release_date,
            "title": Movie.title
        }
        sort_field = allowed_sort_fields.get(sort_by, Movie.release_date)
        if order.lower() == "desc":
            stmt = stmt.order_by(sort_field.desc())
        else:
            stmt = stmt.order_by(sort_field.asc())
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        movies = result.scalars().all()
        logger.info(f"Получено {len(movies)} фильмов по фильтру")
        return movies
