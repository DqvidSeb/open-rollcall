from __future__ import annotations

"""
ScheduleService — lógica de negocio para los horarios de asistencia.

Invariantes garantizadas por este servicio:
  · Solo puede existir un schedule activo a la vez.
  · Activar un schedule desactiva automáticamente el anterior.
  · No se pueden crear dos schedules con el mismo nombre.
  · Los rangos de check-in y check-out son validados por el schema
    antes de llegar al servicio.
"""

import uuid
import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import Schedule
from app.repositories.schedule import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ScheduleRepository(db)

    # ── Lectura ───────────────────────────────────────────────────────────────

    async def get(self, schedule_id: uuid.UUID) -> Schedule:
        obj = await self.repo.get(schedule_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Schedule no encontrado.")
        return obj

    async def list(self, *, offset: int = 0, limit: int = 50) -> list[Schedule]:
        return await self.repo.list(offset=offset, limit=limit)

    async def get_active(self) -> Schedule:
        """
        Retorna el horario activo del sistema.
        Si no hay ninguno configurado, retorna un schedule por defecto
        (Colombia, 08:00–12:00 / 14:00–23:59) para garantizar que
        camera_client siempre tenga una configuración válida.
        """
        from datetime import time

        active = await self.repo.get_active()
        if active:
            return active

        # Fallback en memoria — no se persiste, solo para que el cliente
        # arranque sin error cuando aún no se ha configurado ningún horario.
        logger.warning(
            "No hay ningún schedule activo en BD. "
            "Usando configuración por defecto (América/Bogotá)."
        )
        default = Schedule(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            name="[Por defecto — sin configurar]",
            description="Horario de respaldo. Configure uno en /api/v1/schedules.",
            timezone="America/Bogota",
            check_in_start=time(8, 0),
            check_in_end=time(12, 0),
            checkout_start=time(14, 0),
            checkout_end=time(23, 59, 59),
            is_active=False,
        )
        return default

    # ── Escritura ─────────────────────────────────────────────────────────────

    async def create(self, data: ScheduleCreate) -> Schedule:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un schedule con el nombre '{data.name}'.",
            )

        if data.is_active:
            await self.repo.deactivate_all()

        obj = Schedule(
            name=data.name,
            description=data.description,
            timezone=data.timezone,
            check_in_start=data.check_in_start,
            check_in_end=data.check_in_end,
            checkout_start=data.checkout_start,
            checkout_end=data.checkout_end,
            is_active=data.is_active,
        )
        created = await self.repo.create(obj)
        logger.info("Schedule creado: id=%s name=%r active=%s", created.id, created.name, created.is_active)
        return created

    async def update(self, schedule_id: uuid.UUID, data: ScheduleUpdate) -> Schedule:
        obj = await self.get(schedule_id)

        payload = data.model_dump(exclude_unset=True)

        # Si se cambia el nombre, verificar unicidad
        if "name" in payload:
            conflict = await self.repo.get_by_name(payload["name"])
            if conflict and conflict.id != schedule_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un schedule con el nombre '{payload['name']}'.",
                )

        # Si se activa este schedule, desactivar los demás primero
        if payload.get("is_active") is True:
            await self.repo.deactivate_all()

        updated = await self.repo.update(obj, payload)
        logger.info("Schedule actualizado: id=%s", updated.id)
        return updated

    async def activate(self, schedule_id: uuid.UUID) -> Schedule:
        """Activa el schedule indicado y desactiva todos los demás."""
        obj = await self.get(schedule_id)
        await self.repo.deactivate_all()
        updated = await self.repo.update(obj, {"is_active": True})
        logger.info("Schedule activado: id=%s name=%r", updated.id, updated.name)
        return updated

    async def delete(self, schedule_id: uuid.UUID) -> None:
        obj = await self.get(schedule_id)
        if obj.is_active:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar el schedule activo. Activa otro primero.",
            )
        await self.repo.delete(obj)
        logger.info("Schedule eliminado: id=%s", schedule_id)
