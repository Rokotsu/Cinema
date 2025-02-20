# app/dao/users_dao.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.future import select
from app.models.users import User
from app.dao.base import BaseDAO

class UserDAO(BaseDAO[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Получить пользователя по email."""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except Exception as e:
            raise e
