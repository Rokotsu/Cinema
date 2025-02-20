# tests/conftest.py

import asyncio
import pytest_asyncio
from app.database.base import engine, Base, async_session_maker

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Создает event loop для сессии тестирования."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Перед тестами удаляет и создает таблицы в базе,
    а после тестов очищает базу.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Фикстура, предоставляющая асинхронную сессию для тестов."""
    async with async_session_maker() as session:
        yield session
