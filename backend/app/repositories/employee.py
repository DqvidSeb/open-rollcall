from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.employee import Employee, EmployeeStatus
from app.models.person import Person
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee

    def _active(self):
        return Person.deleted_at.is_(None)

    async def get_with_person(self, id: uuid.UUID) -> Employee | None:
        result = await self.db.execute(
            select(Employee)
            .join(Person, Employee.id == Person.id)
            .options(
                joinedload(Employee.person),
                joinedload(Employee.department),
                joinedload(Employee.position),
                joinedload(Employee.face_encodings),
            )
            .where(Employee.id == id, self._active())
        )
        return result.unique().scalar_one_or_none()

    async def get_by_code(self, code: str) -> Employee | None:
        result = await self.db.execute(
            select(Employee)
            .join(Person, Employee.id == Person.id)
            .where(Employee.employee_code == code.upper(), self._active())
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        department_id: uuid.UUID | None = None,
        status: EmployeeStatus | None = None,
    ) -> list[Employee]:
        stmt = (
            select(Employee)
            .join(Person, Employee.id == Person.id)
            .options(
                joinedload(Employee.person),
                joinedload(Employee.department),
                joinedload(Employee.position),
                joinedload(Employee.face_encodings),
            )
            .where(self._active())
        )
        if department_id:
            stmt = stmt.where(Employee.department_id == department_id)
        if status:
            stmt = stmt.where(Employee.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_active(
        self,
        department_id: uuid.UUID | None = None,
        status: EmployeeStatus | None = None,
    ) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(Employee)
            .join(Person, Employee.id == Person.id)
            .where(self._active())
        )
        if department_id:
            stmt = stmt.where(Employee.department_id == department_id)
        if status:
            stmt = stmt.where(Employee.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()
