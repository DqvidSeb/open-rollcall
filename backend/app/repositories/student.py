from __future__ import annotations

import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models.student import Student, StudentStatus
from app.models.person import Person
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    model = Student

    def _active(self):
        return Person.deleted_at.is_(None)

    async def get_with_person(self, id: uuid.UUID) -> Student | None:
        result = await self.db.execute(
            select(Student)
            .join(Person, Student.id == Person.id)
            .options(
                joinedload(Student.person).joinedload(Person.user),
                joinedload(Student.academic_program),
            )
            .where(Student.id == id, self._active())
        )
        return result.unique().scalar_one_or_none()

    async def get_by_code(self, code: str) -> Student | None:
        result = await self.db.execute(
            select(Student)
            .join(Person, Student.id == Person.id)
            .where(Student.student_code == code.upper(), self._active())
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        academic_program_id: uuid.UUID | None = None,
        status: StudentStatus | None = None,
    ) -> list[Student]:
        stmt = (
            select(Student)
            .join(Person, Student.id == Person.id)
            .options(
                joinedload(Student.person),
                joinedload(Student.academic_program),
            )
            .where(self._active())
        )
        if academic_program_id:
            stmt = stmt.where(Student.academic_program_id == academic_program_id)
        if status:
            stmt = stmt.where(Student.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_active(
        self,
        academic_program_id: uuid.UUID | None = None,
        status: StudentStatus | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Student)
            .join(Person, Student.id == Person.id)
            .where(self._active())
        )
        if academic_program_id:
            stmt = stmt.where(Student.academic_program_id == academic_program_id)
        if status:
            stmt = stmt.where(Student.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()
