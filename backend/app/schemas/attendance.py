from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.attendance_log import AttendanceMethod, EventType


class AttendanceRead(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    full_name: str | None = None
    employee_code: str | None = None
    event_type: EventType
    method: AttendanceMethod
    event_time: datetime
    confidence: float | None
    notes: str | None

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
