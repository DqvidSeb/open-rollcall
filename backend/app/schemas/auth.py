from __future__ import annotations

import uuid
from pydantic import BaseModel, EmailStr, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def flatten_person(cls, data: object) -> object:
        if hasattr(data, "person") and data.person is not None:
            return {
                "id": data.id,
                "full_name": data.person.full_name,
                "email": data.person.email,
                "is_active": data.is_active,
                "is_superuser": data.is_superuser,
            }
        return data


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_superuser: bool = False


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class PaginatedUsers(BaseModel):
    items: list[UserRead]
    total: int
    offset: int
    limit: int
