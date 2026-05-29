from __future__ import annotations

"""
Endpoints de Schedule — gestión de horarios de asistencia.

endpoint GET /active es público para que camera_client.py pueda
consultarlo sin token al arrancar.
"""

import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.schedule import (
    ScheduleActiveRead,
    ScheduleCreate,
    ScheduleRead,
    ScheduleUpdate,
)
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["schedules"])


# Endpoints públicos (sin autenticación)

@router.get(
    "/active",
    response_model=ScheduleActiveRead,
    summary="Obtener horario activo",
    description=(
        "Retorna el horario que está actualmente activo en el sistema. "
        "**Este endpoint es público**: camera_client.py lo consulta al "
        "arrancar para obtener la zona horaria y las ventanas horarias "
        "de check-in y check-out sin necesidad de token. "
        "Si no se ha configurado ningún horario, retorna los valores "
        "por defecto (América/Bogotá, 08:00–12:00 / 14:00–23:59)."
    ),
)
async def get_active_schedule(db: DbSession) -> ScheduleActiveRead:
    service = ScheduleService(db)
    schedule = await service.get_active()
    return ScheduleActiveRead.model_validate(schedule)


# Endpoints protegidos

@router.get(
    "/",
    response_model=list[ScheduleRead],
    summary="Listar todos los horarios",
)
async def list_schedules(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ScheduleRead]:
    """Retorna todos los horarios configurados, paginados."""
    service = ScheduleService(db)
    items = await service.list(offset=offset, limit=limit)
    return [ScheduleRead.model_validate(s) for s in items]


@router.get(
    "/{schedule_id}",
    response_model=ScheduleRead,
    summary="Obtener horario por ID",
)
async def get_schedule(
    schedule_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> ScheduleRead:
    service = ScheduleService(db)
    return ScheduleRead.model_validate(await service.get(schedule_id))


@router.post(
    "/",
    response_model=ScheduleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear horario",
    description=(
        "Crea un nuevo horario de asistencia. "
        "Si `is_active` es `true`, desactiva automáticamente el horario "
        "que estuviera activo antes de crear este. "
        "Los tiempos se expresan en formato `HH:MM:SS` en hora local "
        "(la zona horaria se define en el campo `timezone`)."
    ),
)
async def create_schedule(
    body: ScheduleCreate,
    db: DbSession,
    _: CurrentUserId,
) -> ScheduleRead:
    service = ScheduleService(db)
    return ScheduleRead.model_validate(await service.create(body))


@router.patch(
    "/{schedule_id}",
    response_model=ScheduleRead,
    summary="Actualizar horario (parcial)",
    description=(
        "Actualiza uno o más campos del horario. Solo se modifican los "
        "campos incluidos en el body. Si se envía `is_active: true`, "
        "el horario activo anterior es desactivado automáticamente."
    ),
)
async def update_schedule(
    schedule_id: uuid.UUID,
    body: ScheduleUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> ScheduleRead:
    service = ScheduleService(db)
    return ScheduleRead.model_validate(await service.update(schedule_id, body))


@router.post(
    "/{schedule_id}/activate",
    response_model=ScheduleRead,
    summary="Activar horario",
    description=(
        "Marca el horario indicado como activo y desactiva cualquier otro. "
        "Atajo conveniente que no requiere enviar el body completo."
    ),
)
async def activate_schedule(
    schedule_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> ScheduleRead:
    service = ScheduleService(db)
    return ScheduleRead.model_validate(await service.activate(schedule_id))


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar horario",
    description=(
        "Elimina el horario. No se puede eliminar el horario activo: "
        "primero activa otro y luego elimina éste."
    ),
)
async def delete_schedule(
    schedule_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    service = ScheduleService(db)
    await service.delete(schedule_id)
