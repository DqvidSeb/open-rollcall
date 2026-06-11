from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Person(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "person"

    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["User | None"] = relationship(
        "User", back_populates="person", uselist=False, cascade="all, delete-orphan"
    )
    employee: Mapped["Employee | None"] = relationship(
        "Employee", back_populates="person", uselist=False, cascade="all, delete-orphan"
    )
    student: Mapped["Student | None"] = relationship(
        "Student", back_populates="person", uselist=False, cascade="all, delete-orphan"
    )
    face_encodings: Mapped[list["FaceEncoding"]] = relationship(
        "FaceEncoding", back_populates="person", cascade="all, delete-orphan"
    )
    attendance_logs: Mapped[list["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="person", cascade="all, delete-orphan"
    )

    @property
    def is_enrolled(self) -> bool:
        return len(self.face_encodings) > 0

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Person id={self.id} name={self.full_name!r}>"
