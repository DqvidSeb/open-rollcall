from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from app.models.employee import Employee
from app.models.person import Person
from app.models.student import Student
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    model = Person

    def _active(self):
        return Person.deleted_at.is_(None)

    async def get_active(self, id: uuid.UUID) -> Person | None:
        result = await self.db.execute(
            select(Person)
            .options(joinedload(Person.user), joinedload(Person.employee), joinedload(Person.student))
            .where(Person.id == id, self._active())
        )
        return result.scalar_one_or_none()

    def is_employee_or_student(self):
        """Excludes plain `Person` records that only back a system `User`
        (admins/staff accounts) — the persons table only lists employees
        and students."""
        return or_(Person.employee.has(), Person.student.has())

    async def list_with_relations(self, *, offset: int = 0, limit: int = 50) -> list[Person]:
        result = await self.db.execute(
            select(Person)
            .options(
                joinedload(Person.employee).joinedload(Employee.department),
                joinedload(Person.employee).joinedload(Employee.position),
                joinedload(Person.student).joinedload(Student.academic_program),
            )
            .where(self._active(), self.is_employee_or_student())
            .order_by(Person.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def get_by_email(self, email: str) -> Person | None:
        result = await self.db.execute(
            select(Person).where(Person.email == email.lower(), self._active())
        )
        return result.scalar_one_or_none()

    async def soft_delete_cascade(self, person: Person) -> None:
        """
        Soft delete en cascada.

        - Person.deleted_at = now  →  la oculta de TODAS las queries
          (employees y users ya hacen JOIN con person y filtran deleted_at IS NULL)
        - User.is_active = False   →  bloquea login inmediatamente aunque
          el token aún no haya expirado
        - Employee no necesita campo propio: sus repositorios filtran
          por Person.deleted_at, por lo que queda invisible automáticamente.
        """
        now = datetime.now(UTC)
        person.deleted_at = now

        if person.user is not None:
            person.user.is_active = False

        await self.db.flush()
