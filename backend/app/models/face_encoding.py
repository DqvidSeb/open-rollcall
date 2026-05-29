from __future__ import annotations

"""
FaceEncoding — embeddings biométricos de un employee.
Solo se guardan vectores, nunca fotos originales.
ArcFace produce embeddings de 512 dimensiones.
"""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

ARCFACE_DIM = 512


class FaceEncoding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "face_encoding"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(ARCFACE_DIM), nullable=False)
    sample_index: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    employee: Mapped["Employee"] = relationship(  # noqa: F821
        "Employee", back_populates="face_encodings"
    )

    def __repr__(self) -> str:
        return f"<FaceEncoding id={self.id} employee_id={self.employee_id} sample={self.sample_index}>"
