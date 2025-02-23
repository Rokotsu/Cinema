from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.future import select
from app.models.users import User
from app.dao.base import BaseDAO

class UserDAO(BaseDAO[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except Exception as e:
            raise e

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).where(User.username == username))
            return result.scalars().first()
        except Exception as e:
            raise e
