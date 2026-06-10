from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class PersonCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None


class PersonUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class PersonRead(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    full_name: str
    email: str | None
    phone: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonListItem(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    person_type: str | None
    """ "employee" | "student" | None """
    code: str | None
    """employee_code or student_code, depending on person_type"""
    group_name: str | None
    """department name (employee) or academic program name (student)"""
    status: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPersons(BaseModel):
    items: list[PersonListItem]
    total: int
    offset: int
    limit: int
