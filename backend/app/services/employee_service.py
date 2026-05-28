from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.employee import Employee
from app.models.person import Person
from app.models.position import Position
from app.repositories.base import BaseRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.person import PersonRepository
from app.schemas.employee import (
    DepartmentCreate, DepartmentUpdate,
    EmployeeCreate, EmployeeUpdate,
    PositionCreate, PositionUpdate,
)


class DepartmentRepository(BaseRepository[Department]):
    model = Department


class PositionRepository(BaseRepository[Position]):
    model = Position


class EmployeeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.emp_repo = EmployeeRepository(db)
        self.person_repo = PersonRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.pos_repo = PositionRepository(db)

    # ── Departments ────────────────────────────────────────────────────────────

    async def create_department(self, data: DepartmentCreate) -> Department:
        dept = Department(name=data.name.strip(), description=data.description)
        return await self.dept_repo.create(dept)

    async def get_department(self, dept_id: uuid.UUID) -> Department:
        dept = await self.dept_repo.get(dept_id)
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Department not found")
        return dept

    async def list_departments(self, *, offset: int = 0, limit: int = 50) -> tuple[list[Department], int]:
        items = await self.dept_repo.list(offset=offset, limit=limit)
        total = await self.dept_repo.count()
        return items, total

    async def update_department(self, dept_id: uuid.UUID, data: DepartmentUpdate) -> Department:
        dept = await self.get_department(dept_id)
        return await self.dept_repo.update(dept, data.model_dump(exclude_unset=True))

    async def delete_department(self, dept_id: uuid.UUID) -> None:
        dept = await self.get_department(dept_id)
        await self.dept_repo.delete(dept)

    # ── Positions ──────────────────────────────────────────────────────────────

    async def create_position(self, data: PositionCreate) -> Position:
        pos = Position(name=data.name.strip(), description=data.description)
        return await self.pos_repo.create(pos)

    async def get_position(self, pos_id: uuid.UUID) -> Position:
        pos = await self.pos_repo.get(pos_id)
        if not pos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Position not found")
        return pos

    async def list_positions(self, *, offset: int = 0, limit: int = 50) -> tuple[list[Position], int]:
        items = await self.pos_repo.list(offset=offset, limit=limit)
        total = await self.pos_repo.count()
        return items, total

    async def update_position(self, pos_id: uuid.UUID, data: PositionUpdate) -> Position:
        pos = await self.get_position(pos_id)
        return await self.pos_repo.update(pos, data.model_dump(exclude_unset=True))

    async def delete_position(self, pos_id: uuid.UUID) -> None:
        pos = await self.get_position(pos_id)
        await self.pos_repo.delete(pos)

    # ── Employees ──────────────────────────────────────────────────────────────

    async def create(self, data: EmployeeCreate) -> Employee:
        if data.email:
            existing = await self.person_repo.get_by_email(data.email)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Email already registered")
        if await self.emp_repo.get_by_code(data.employee_code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Employee code '{data.employee_code}' already in use")

        person = Person(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower() if data.email else None,
            phone=data.phone,
        )
        await self.person_repo.create(person)

        employee = Employee(
            id=person.id,
            employee_code=data.employee_code,
            department_id=data.department_id,
            position_id=data.position_id,
            status=data.status,
            hire_date=data.hire_date,
        )
        await self.emp_repo.create(employee)
        # Re-fetch con todas las relaciones cargadas (person, department, position, face_encodings)
        return await self.emp_repo.get_with_person(employee.id)  # type: ignore[return-value]

    async def get(self, employee_id: uuid.UUID) -> Employee:
        emp = await self.emp_repo.get_with_person(employee_id)
        if not emp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employee not found")
        return emp

    async def list(
        self, *, offset: int = 0, limit: int = 50,
        department_id: uuid.UUID | None = None,
        status=None,
    ) -> tuple[list[Employee], int]:
        items = await self.emp_repo.list_active(
            offset=offset, limit=limit,
            department_id=department_id, status=status,
        )
        total = await self.emp_repo.count_active(
            department_id=department_id, status=status,
        )
        return items, total

    async def update(self, employee_id: uuid.UUID, data: EmployeeUpdate) -> Employee:
        emp = await self.get(employee_id)
        update = data.model_dump(exclude_unset=True)
        person_fields = {k: update.pop(k) for k in ("first_name", "last_name", "email", "phone") if k in update}
        if person_fields:
            await self.person_repo.update(emp.person, person_fields)
        if update:
            await self.emp_repo.update(emp, update)
        await self.db.refresh(emp)
        return emp

    async def delete(self, employee_id: uuid.UUID) -> None:
        emp = await self.get(employee_id)
        await self.person_repo.soft_delete_cascade(emp.person)
