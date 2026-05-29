from __future__ import annotations

"""
AttendanceLog — registro inmutable de eventos de asistencia.
Solo INSERT, nunca UPDATE. Correcciones se hacen con un nuevo registro method=override.
"""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.employee import Employee


class EventType(str, enum.Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class AttendanceMethod(str, enum.Enum):
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    OVERRIDE = "override"


class AttendanceLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "attendance_log"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(
            EventType,
            name="event_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )

    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(
            AttendanceMethod,
            name="attendance_method",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        default=AttendanceMethod.FACE_RECOGNITION,
        nullable=False,
    )

    event_time: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    snapshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete="SET NULL"),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employee: Mapped[Employee] = relationship(
        "Employee",
        back_populates="attendance_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<AttendanceLog id={self.id} "
            f"employee_id={self.employee_id} "
            f"type={self.event_type}>"
        )