# app/api/v1/movies.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.movies import MovieCreate, MovieRead, MovieUpdate
from app.services.movies_service import MovieService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import MovieNotFoundException

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
