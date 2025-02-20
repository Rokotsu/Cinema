# app/services/movies_service.py

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def get_movie(self, db: AsyncSession, movie_id: int) -> Optional[Movie]:
        movie = await self.movie_dao.get_by_id(db, movie_id)
        if not movie:
            logger.warning(f"Фильм с id {movie_id} не найден")
            raise MovieNotFoundException()
        return movie

    async def list_movies(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Movie]:
        movies = await self.movie_dao.list(db, skip, limit)
        logger.info(f"Получено {len(movies)} фильмов")
        return movies
