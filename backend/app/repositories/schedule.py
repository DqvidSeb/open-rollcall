from __future__ import annotations

"""
ScheduleRepository — acceso a datos para la tabla schedule.
"""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import Schedule
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    model = Schedule

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_active(self) -> Schedule | None:
        """Retorna el horario marcado como activo (máximo uno en el sistema)."""
        stmt = select(Schedule).where(Schedule.is_active.is_(True)).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_all(self) -> None:
        """
        Desactiva todos los schedules.
        Llamar antes de activar uno nuevo para garantizar unicidad del activo.
        """
        stmt = (
            update(Schedule)
            .where(Schedule.is_active.is_(True))
            .values(is_active=False)
        )
        await self.db.execute(stmt)

    async def get_by_name(self, name: str) -> Schedule | None:
        stmt = select(Schedule).where(Schedule.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
