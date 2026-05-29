from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id: uuid.UUID) -> T | None:
        return await self.db.get(self.model, id)

    async def get_or_raise(self, id: uuid.UUID) -> T:
        obj = await self.get(id)
        if obj is None:
            raise ValueError(f"{self.model.__name__} id={id} not found")
        return obj

    async def list(self, *, offset: int = 0, limit: int = 50, filters: list[Any] | None = None) -> list[T]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: list[Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.where(*filters)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T, data: dict[str, Any]) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def soft_delete(self, obj: T) -> T:
        obj.soft_delete()  # type: ignore[attr-defined]
        await self.db.flush()
        return obj
