from __future__ import annotations

"""
Schedule — turno/horario de asistencia.

Define las ventanas horarias válidas para check-in y check-out,
la zona horaria del dispositivo que ejecuta el cliente de cámara,
y si es el horario activo/por-defecto de la instalación.

Diseño normalizado (1FN–3FN):
  · Cada atributo es atómico y depende únicamente de la PK (id).
  · No hay dependencias transitivas: timezone, check_in_start, etc.
    dependen directamente del schedule, no entre sí.
  · Los horarios de inicio/fin se almacenan como TIME WITH TIME ZONE
    (solo la hora, sin fecha); la fecha la aporta el reloj local al
    momento de evaluar si un evento cae en ventana.
"""

import uuid

from sqlalchemy import Boolean, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Nombre descriptivo: "Turno mañana", "Jornada completa", etc.
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    # Descripción opcional para el panel de administración.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Zona horaria IANA del nodo que ejecuta camera_client.py.
    # Ejemplos: "America/Bogota", "America/New_York", "Europe/Madrid".
    # Cada instalación puede correr en una TZ diferente.
    timezone: Mapped[str] = mapped_column(
        String(60), nullable=False, default="America/Bogota"
    )

    # ── Ventana check-in ──────────────────────────────────────────────────────
    # Hora de inicio a partir de la cual se acepta un check-in (inclusive).
    check_in_start: Mapped[object] = mapped_column(
        Time(timezone=False), nullable=False
    )
    # Hora de fin hasta la cual se acepta un check-in (exclusive).
    check_in_end: Mapped[object] = mapped_column(
        Time(timezone=False), nullable=False
    )

    # ── Ventana check-out ─────────────────────────────────────────────────────
    checkout_start: Mapped[object] = mapped_column(
        Time(timezone=False), nullable=False
    )
    checkout_end: Mapped[object] = mapped_column(
        Time(timezone=False), nullable=False
    )

    # Solo puede haber un schedule activo (el predeterminado del sistema).
    # La unicidad del "activo" se garantiza a nivel de servicio
    # (antes de activar uno, se desactivan los demás).
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<Schedule id={self.id} name={self.name!r} "
            f"tz={self.timezone!r} active={self.is_active}>"
        )
