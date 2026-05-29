from __future__ import annotations

"""Endpoints de asistencia."""

import uuid
from datetime import date, datetime

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.attendance import (
    AttendanceManualCreate,
    AttendanceRead,
    AttendanceSummary,
    PaginatedAttendance,
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post(
    "/manual",
    response_model=AttendanceRead,
    status_code=201,
    summary="Registrar asistencia manualmente",
)
async def manual_attendance(
    body: AttendanceManualCreate,
    db: DbSession,
    current_user_id: CurrentUserId,
) -> AttendanceRead:
    service = AttendanceService(db)
    att = await service.record_manual(body, recorded_by=current_user_id)
    return AttendanceRead.model_validate(att)


@router.get(
    "/summary",
    response_model=list[AttendanceSummary],
    summary="Resumen diario de asistencia",
)
async def daily_summary(
    db: DbSession,
    _: CurrentUserId,
    target_date: date = Query(default_factory=date.today),
) -> list[AttendanceSummary]:
    """Retorna check-in, check-out y horas trabajadas por empleado en un día."""
    service = AttendanceService(db)
    return await service.get_daily_summary(target_date)


@router.get(
    "/employee/{employee_id}",
    response_model=PaginatedAttendance,
    summary="Historial de asistencia de un empleado",
)
async def employee_attendance(
    employee_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> PaginatedAttendance:
    offset = (page - 1) * page_size
    service = AttendanceService(db)
    items, total = await service.list_by_employee(
        employee_id,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        limit=page_size,
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedAttendance(
        items=[AttendanceRead.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
