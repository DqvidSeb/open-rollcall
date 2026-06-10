from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator

from app.models.student import StudentStatus


# ── Academic program ─────────────────────────────────────────────────────────

class AcademicProgramCreate(BaseModel):
    name: str
    description: str | None = None


class AcademicProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class AcademicProgramRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedAcademicPrograms(BaseModel):
    items: list[AcademicProgramRead]
    total: int
    offset: int
    limit: int


# ── Student ────────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    student_code: str
    academic_program_id: uuid.UUID | None = None
    grade_level: str | None = None
    status: StudentStatus = StudentStatus.ACTIVE
    enrollment_date: date | None = None

    @field_validator("student_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return v.strip().upper()


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    academic_program_id: uuid.UUID | None = None
    grade_level: str | None = None
    status: StudentStatus | None = None
    enrollment_date: date | None = None


class StudentRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    student_code: str
    academic_program_id: uuid.UUID | None
    academic_program_name: str | None = None
    grade_level: str | None
    status: StudentStatus
    enrollment_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedStudents(BaseModel):
    items: list[StudentRead]
    total: int
    offset: int
    limit: int
