import sys
from logging.config import fileConfig
from os.path import abspath, dirname

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

# Импортируем модели, чтобы Alembic мог их видеть
from app.models.users import User
from app.models.movies import Movie
from app.models.subscriptions import Subscription
from app.models.payments import Payment
from app.database.base import Base
from app.core.config import settings

# Получаем объект конфигурации Alembic
config = context.config
config.set_main_option("sqlalchemy.url", f"{settings.DATABASE_URL}?async_fallback=True")

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData для Alembic
target_metadata = Base.metadata

# Создаём асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool
)

async def run_migrations_online():
    """Запуск миграций в онлайн-режиме (с подключением к БД)."""
    async with engine.begin() as connection:
        # Настраиваем Alembic через lambda, чтобы избежать передачи connection дважды
        await connection.run_sync(
            lambda conn: context.configure(connection=conn, target_metadata=target_metadata)
        )
        # Запускаем миграции, также оборачивая вызов в lambda
        await connection.run_sync(lambda conn: context.run_migrations())

if context.is_offline_mode():
    def run_migrations_offline():
        """Запуск миграций в оффлайн-режиме (без подключения к БД)."""
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
