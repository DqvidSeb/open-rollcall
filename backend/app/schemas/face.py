from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class EnrollBody(BaseModel):
    images_base64: list[str] = Field(..., min_length=1)


class FaceEnrollResponse(BaseModel):
    employee_id: uuid.UUID
    samples_captured: int
    message: str


class FaceVerifyRequest(BaseModel):
    image_base64: str


class FaceVerifyResponse(BaseModel):
    recognized: bool
    employee_id: uuid.UUID | None = None
    full_name: str | None = None
    employee_code: str | None = None
    confidence: float | None = None
    message: str
