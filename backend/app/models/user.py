"""
User — administrador del sistema. Especialización 1:1 de Person.
Su PK es el mismo UUID de la fila Person correspondiente.
"""

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.elements import quoted_name

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    # "user" es palabra reservada en PostgreSQL — se fuerza el quoting
    __tablename__ = quoted_name("user", True)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("person.id", ondelete="CASCADE"),
        primary_key=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    person: Mapped["Person"] = relationship(  # noqa: F821
        "Person", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} superuser={self.is_superuser}>"
