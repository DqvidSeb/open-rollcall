from __future__ import annotations

"""Position — catálogo de cargos/puestos."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Position(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "position"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    employees: Mapped[list["Employee"]] = relationship(  # noqa: F821
        "Employee", back_populates="position"
    )

    def __repr__(self) -> str:
        return f"<Position id={self.id} name={self.name!r}>"
