from __future__ import annotations

"""AcademicProgram — catálogo de programas académicos (carreras, grados, etc.)."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AcademicProgram(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "academic_program"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    students: Mapped[list["Student"]] = relationship(  # noqa: F821
        "Student", back_populates="academic_program"
    )

    def __repr__(self) -> str:
        return f"<AcademicProgram id={self.id} name={self.name!r}>"
