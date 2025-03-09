from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import (
    UserNotFoundException,
    AuthenticationException,
    InvalidTokenException
)
from app.models.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = "Bearer"  # Фиктивное значение

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Токен истёк. Пожалуйста, авторизуйтесь снова")
    except jwt.PyJWTError:
        raise InvalidTokenException("Неверный токен. Пожалуйста, проверьте данные авторизации")

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> User:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
    else:
        token = request.cookies.get("access_token")
    if not token:
        raise AuthenticationException("Необходима авторизация")
    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise AuthenticationException("Неверные учетные данные")
    from app.services.users_service import UserService
    user_service = UserService()
    return await user_service.get_user_by_id(db, int(user_id))
