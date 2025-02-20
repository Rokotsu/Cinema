# conftest.py

import asyncio
import pytest
from httpx import AsyncClient

# Импортируем приложение FastAPI
from app.main import app
# Импортируем созданный асинхронный движок, базовый класс и session maker
from app.database.base import engine, Base, async_session_maker


@pytest.fixture(scope="session")
def event_loop():
    """
    Создаем новый event loop для всей сессии тестирования.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Перед запуском тестов: очищаем тестовую базу, создаем все таблицы.
    После тестов: удаляем все таблицы.
    """
    async with engine.begin() as conn:
        # Удаляем таблицы, если они существуют, и создаем их заново
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def async_client():
    """
    Фикстура для асинхронного тестового клиента FastAPI с использованием httpx.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """
    Фикстура, предоставляющая сессию для взаимодействия с БД.
    """
    async with async_session_maker() as session:
        yield session
