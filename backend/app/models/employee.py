from __future__ import annotations

"""
Employee — persona que pasa lista. Especialización 1:1 de Person.
Su PK es el mismo UUID de la fila Person correspondiente.
"""

import enum
import uuid

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class Employee(Base, TimestampMixin):
    __tablename__ = "employee"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("person.id", ondelete="CASCADE"),
        primary_key=True,
    )
    employee_code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    position_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("position.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(EmployeeStatus, name="employee_status", values_callable=lambda x: [e.value for e in x]),
        default=EmployeeStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    hire_date: Mapped[object] = mapped_column(Date, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    person: Mapped["Person"] = relationship(  # noqa: F821
        "Person", back_populates="employee"
    )
    department: Mapped["Department | None"] = relationship(  # noqa: F821
        "Department", back_populates="employees"
    )
    position: Mapped["Position | None"] = relationship(  # noqa: F821
        "Position", back_populates="employees"
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} code={self.employee_code!r}>"
