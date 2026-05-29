from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.attendance_log import AttendanceMethod, EventType


class AttendanceRead(BaseModel):
    # ── Datos del log ─────────────────────────────────────────────────────────
    id: uuid.UUID
    event_type: EventType
    method: AttendanceMethod
    event_time: datetime
    confidence: float | None = None
    notes: str | None = None

    # ── Datos del empleado/persona enriquecidos por el endpoint ───────────────
    # Estos campos NO existen en el modelo AttendanceLog. Los rellena la capa
    # de servicio/endpoint para que el cliente pueda mostrar la info sin tener
    # que hacer un GET adicional al empleado.
    employee_id: uuid.UUID
    employee_code: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    department: str | None = None
    position: str | None = None
    status: str | None = None
    hire_date: str | None = None

    model_config = {"from_attributes": True}


class AttendanceManualCreate(BaseModel):
    employee_id: uuid.UUID
    event_type: EventType
    event_time: datetime | None = None
    notes: str | None = None


class AttendanceSummary(BaseModel):
    employee_id: uuid.UUID
    full_name: str
    employee_code: str
    date: str
    check_in_time: datetime | None
    check_out_time: datetime | None
    total_hours: float | None


class PaginatedAttendance(BaseModel):
    items: list[AttendanceRead]
    total: int
    page: int
    page_size: int
    total_pages: int
