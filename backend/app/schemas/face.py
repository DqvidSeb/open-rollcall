from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field

PersonType = Literal["employee", "student"]


class EnrollBody(BaseModel):
    images_base64: list[str] = Field(..., min_length=1)
    # True solo cuando el cliente ya detecto, recorto y alineo el rostro
    # (camera_client.py con YuNet). Los clientes web envian el frame completo
    # y dejan la deteccion/alineacion al servidor.
    pre_cropped: bool = False


class FaceEnrollResponse(BaseModel):
    person_id: uuid.UUID
    samples_captured: int
    message: str


class FaceVerifyRequest(BaseModel):
    image_base64: str
    # Ver nota en EnrollBody: True = rostro ya recortado/alineado por el cliente.
    pre_cropped: bool = False


class FaceVerifyResponse(BaseModel):
    recognized: bool
    person_id: uuid.UUID | None = None
    person_type: PersonType | None = None
    full_name: str | None = None
    code: str | None = None
    confidence: float | None = None
    message: str


class FaceStatusResponse(BaseModel):
    person_id: uuid.UUID
    enrolled: bool
    samples: int
