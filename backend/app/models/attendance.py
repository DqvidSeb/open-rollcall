"""
Attendance model — registro de entradas y salidas de cada persona.
"""

import enum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AttendanceType(str, enum.Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class AttendanceMethod(str, enum.Enum):
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"          # ingreso manual por un admin
    OVERRIDE = "override"      # corrección retroactiva


class Attendance(Base, TimestampMixin):
    """
    Cada fila = un evento de asistencia (entrada o salida).
    El par check_in / check_out se vincula por session_date + person_id
    a nivel de consulta, no con FK directa, para simplificar el modelo.
    """

    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[AttendanceType] = mapped_column(
        Enum(AttendanceType, name="attendance_type"),
        nullable=False,
        index=True,
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(AttendanceMethod, name="attendance_method"),
        default=AttendanceMethod.FACE_RECOGNITION,
        nullable=False,
    )

    # Timestamp exacto del evento (con zona horaria)
    event_time: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Confianza del reconocimiento (0.0–1.0); NULL para entradas manuales
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Snapshot de la cámara (ruta relativa al frame capturado, opcional)
    snapshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Notas del admin para entradas manuales / overrides
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    person: Mapped["Person"] = relationship(  # noqa: F821
        "Person",
        back_populates="attendances",
    )

    def __repr__(self) -> str:
        return (
            f"<Attendance id={self.id} person_id={self.person_id} "
            f"type={self.event_type} time={self.event_time}>"
        )
