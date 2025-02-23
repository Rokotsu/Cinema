import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.users_dao import UserDAO
from app.schemas.users import UserCreate, UserUpdate
from app.models.users import User
from app.core.security import get_password_hash
from app.exceptions.custom_exceptions import UserAlreadyExistsException, UserNotFoundException

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_dao: Optional[UserDAO] = None):
        self.user_dao = user_dao or UserDAO()

    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        existing_user = await self.user_dao.get_by_email(db, user_in.email)
        if existing_user:
            logger.error(f"Регистрация: пользователь с email {user_in.email} уже существует")
            raise UserAlreadyExistsException()
        user_data = user_in.dict()
        user_data["hashed_password"] = get_password_hash(user_data["password"])
        user_data.pop("password")
        user = await self.user_dao.create(db, user_data)
        logger.info(f"Зарегистрирован новый пользователь с id {user.id}")
        return user

    async def update_user(self, db: AsyncSession, user_id: int, user_in: UserUpdate) -> User:
        user = await self.user_dao.get_by_id(db, user_id)
        if not user:
            logger.error(f"Обновление: пользователь с id {user_id} не найден")
            raise UserNotFoundException()
        user_data = user_in.dict(exclude_unset=True)
        if "password" in user_data and user_data["password"]:
            user_data["hashed_password"] = get_password_hash(user_data["password"])
            del user_data["password"]
        user = await self.user_dao.update(db, user, user_data)
        logger.info(f"Обновлены данные пользователя с id {user.id}")
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        user = await self.user_dao.get_by_id(db, user_id)
        if not user:
            logger.warning(f"Пользователь с id {user_id} не найден")
            raise UserNotFoundException()
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User:
        user = await self.user_dao.get_by_email(db, email)
        if not user:
            logger.warning(f"Пользователь с email {email} не найден")
            raise UserNotFoundException()
        return user

    # Новый метод для логина по username:
    async def get_user_by_username(self, db: AsyncSession, username: str) -> User:
        user = await self.user_dao.get_by_username(db, username)
        if not user:
            logger.warning(f"Пользователь с username {username} не найден")
            raise UserNotFoundException()
        return user
