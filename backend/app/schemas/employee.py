from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator

from app.models.employee import EmployeeStatus


# ── Department ─────────────────────────────────────────────────────────────────

class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class DepartmentRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedDepartments(BaseModel):
    items: list[DepartmentRead]
    total: int
    offset: int
    limit: int


# ── Position ───────────────────────────────────────────────────────────────────

class PositionCreate(BaseModel):
    name: str
    description: str | None = None


class PositionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class PositionRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPositions(BaseModel):
    items: list[PositionRead]
    total: int
    offset: int
    limit: int


# ── Employee ───────────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    employee_code: str
    department_id: uuid.UUID | None = None
    position_id: uuid.UUID | None = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hire_date: date | None = None

    @field_validator("employee_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return v.strip().upper()


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    department_id: uuid.UUID | None = None
    position_id: uuid.UUID | None = None
    status: EmployeeStatus | None = None
    hire_date: date | None = None


class EmployeeRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    employee_code: str
    department_id: uuid.UUID | None
    position_id: uuid.UUID | None
    department_name: str | None = None
    position_name: str | None = None
    status: EmployeeStatus
    hire_date: date | None
    is_enrolled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedEmployees(BaseModel):
    items: list[EmployeeRead]
    total: int
    offset: int
    limit: int
