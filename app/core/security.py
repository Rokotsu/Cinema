# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Создаём контекст для хэширования паролей с использованием bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширует переданный пароль с использованием алгоритма bcrypt.

    :param password: Пароль в виде строки.
    :return: Хэшированная строка пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли открытый пароль его хэшированному варианту.

    :param plain_password: Открытый пароль.
    :param hashed_password: Хэшированная версия пароля.
    :return: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT-токен с данными payload и временем истечения.

    :param data: Словарь с данными, которые будут зашифрованы в токене.
    :param expires_delta: Временной интервал до истечения токена. По умолчанию 15 минут.
    :return: Закодированный JWT-токен в виде строки.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Декодирует JWT-токен и возвращает данные payload.
    При ошибке декодирования возвращает пустой словарь.

    :param token: JWT-токен в виде строки.
    :return: Данные из токена (словарь) или пустой словарь при ошибке.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return {}
