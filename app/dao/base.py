# app/dao/base.py

import enum
from typing import Any, Dict
from collections import deque
from typing import Type, TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


def _normalize_obj_in(obj_in: Dict[str, Any]) -> Dict[str, Any]:
    """
    Преобразует словарь, заменяя все значения, являющиеся экземплярами enum,
    на их строковое представление в верхнем регистре.
    """
    return {k: (v.value.upper() if isinstance(v, enum.Enum) else v) for k, v in obj_in.items()}

class BaseDAO(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        normalized_obj_in = _normalize_obj_in(obj_in)
        db_obj = self.model(**normalized_obj_in)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        normalized_obj_in = _normalize_obj_in({k: v for k, v in obj_in.items() if v is not None})
        for field, value in normalized_obj_in.items():
            setattr(db_obj, field, value)
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

class BaseDAO(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Получить объект по ID."""
        try:
            result = await db.execute(select(self.model).where(self.model.id == id))
            return result.scalars().first()
        except SQLAlchemyError as e:
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
        normalized_obj_in = _normalize_obj_in(obj_in)
        db_obj = self.model(**normalized_obj_in)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Обновить объект. Обновляются только поля, переданные в obj_in (если они не None)."""
        normalized_obj_in = _normalize_obj_in({k: v for k, v in obj_in.items() if v is not None})
        for field, value in normalized_obj_in.items():
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
