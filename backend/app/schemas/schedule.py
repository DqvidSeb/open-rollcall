from __future__ import annotations

"""
Schemas Pydantic para Schedule (horarios de asistencia).
"""

import uuid
from datetime import time, datetime

from pydantic import BaseModel, Field, field_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


# ── Validador reutilizable ────────────────────────────────────────────────────

def _validate_timezone(tz: str) -> str:
    """Verifica que la cadena sea un identificador IANA válido."""
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, KeyError):
        raise ValueError(
            f"'{tz}' no es una zona horaria IANA válida. "
            "Ejemplos: 'America/Bogota', 'Europe/Madrid', 'UTC'."
        )
    return tz


# ── Request schemas ───────────────────────────────────────────────────────────

class ScheduleCreate(BaseModel):
    """
    Payload para crear un nuevo horario.

    Las horas se expresan en tiempo local (sin zona horaria adjunta).
    La zona horaria del nodo se indica en el campo `timezone`.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        examples=["Jornada completa", "Turno mañana"],
        description="Nombre descriptivo del horario.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Descripción opcional visible en el panel de administración.",
    )
    timezone: str = Field(
        default="America/Bogota",
        examples=["America/Bogota", "America/New_York", "Europe/Madrid", "UTC"],
        description=(
            "Identificador IANA de la zona horaria del nodo "
            "que ejecuta camera_client.py."
        ),
    )
    check_in_start: time = Field(
        ...,
        examples=["08:00:00"],
        description="Hora de inicio de la ventana de check-in (inclusive).",
    )
    check_in_end: time = Field(
        ...,
        examples=["12:00:00"],
        description="Hora de fin de la ventana de check-in (exclusive).",
    )
    checkout_start: time = Field(
        ...,
        examples=["14:00:00"],
        description="Hora de inicio de la ventana de check-out (inclusive).",
    )
    checkout_end: time = Field(
        ...,
        examples=["23:59:59"],
        description="Hora de fin de la ventana de check-out (exclusive).",
    )
    is_active: bool = Field(
        default=False,
        description=(
            "Si se activa este horario, el servicio lo marcará como predeterminado "
            "y desactivará cualquier otro horario activo."
        ),
    )

    @field_validator("timezone")
    @classmethod
    def validate_tz(cls, v: str) -> str:
        return _validate_timezone(v)

    @field_validator("check_in_end")
    @classmethod
    def checkin_end_after_start(cls, v: time, info) -> time:
        start = info.data.get("check_in_start")
        if start and v <= start:
            raise ValueError("check_in_end debe ser posterior a check_in_start.")
        return v

    @field_validator("checkout_end")
    @classmethod
    def checkout_end_after_start(cls, v: time, info) -> time:
        start = info.data.get("checkout_start")
        if start and v <= start:
            raise ValueError("checkout_end debe ser posterior a checkout_start.")
        return v


class ScheduleUpdate(BaseModel):
    """Actualización parcial — todos los campos son opcionales."""
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    timezone: str | None = None
    check_in_start: time | None = None
    check_in_end: time | None = None
    checkout_start: time | None = None
    checkout_end: time | None = None
    is_active: bool | None = None

    @field_validator("timezone")
    @classmethod
    def validate_tz(cls, v: str | None) -> str | None:
        if v is not None:
            _validate_timezone(v)
        return v


# ── Response schema ───────────────────────────────────────────────────────────

class ScheduleRead(BaseModel):
    """Representación completa de un horario tal como se almacena en BD."""
    id: uuid.UUID
    name: str
    description: str | None
    timezone: str
    check_in_start: time
    check_in_end: time
    checkout_start: time
    checkout_end: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Lightweight schema para el camera_client ─────────────────────────────────

class ScheduleActiveRead(BaseModel):
    """
    Payload mínimo que consume camera_client.py al arrancar.
    Solo incluye los campos necesarios para operar la cámara.
    """
    id: uuid.UUID
    name: str
    timezone: str
    check_in_start: time
    check_in_end: time
    checkout_start: time
    checkout_end: time

    model_config = {"from_attributes": True}
