# File: app/dao/movies_dao.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.movies import Movie
from app.dao.base import BaseDAO

class MovieDAO(BaseDAO[Movie]):
    def __init__(self):
        super().__init__(Movie)
