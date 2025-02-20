from typing import Type, TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseDAO(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Получить объект по ID."""
        try:
            result = await db.execute(select(self.model).where(self.model.id == id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            # Здесь можно добавить логирование ошибки
            raise e

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список объектов с пагинацией."""
        try:
            result = await db.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise e

    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """Создать новый объект в базе данных."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Обновить объект. Обновляются только поля, значение которых не None."""
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    async def delete(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Удалить объект по его ID."""
        db_obj = await self.get_by_id(db, id)
        if db_obj:
            try:
                await db.delete(db_obj)
                await db.commit()
                return db_obj
            except SQLAlchemyError as e:
                await db.rollback()
                raise e
        return None
