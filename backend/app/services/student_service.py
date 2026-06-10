from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic_program import AcademicProgram
from app.models.person import Person
from app.models.student import Student
from app.repositories.base import BaseRepository
from app.repositories.person import PersonRepository
from app.repositories.student import StudentRepository
from app.schemas.student import (
    AcademicProgramCreate, AcademicProgramUpdate,
    StudentCreate, StudentUpdate,
)


class AcademicProgramRepository(BaseRepository[AcademicProgram]):
    model = AcademicProgram


class StudentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.student_repo = StudentRepository(db)
        self.person_repo = PersonRepository(db)
        self.program_repo = AcademicProgramRepository(db)

    # ── Academic programs ──────────────────────────────────────────────────────

    async def create_program(self, data: AcademicProgramCreate) -> AcademicProgram:
        program = AcademicProgram(name=data.name.strip(), description=data.description)
        return await self.program_repo.create(program)

    async def get_program(self, program_id: uuid.UUID) -> AcademicProgram:
        program = await self.program_repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Academic program not found")
        return program

    async def list_programs(self, *, offset: int = 0, limit: int = 50) -> tuple[list[AcademicProgram], int]:
        items = await self.program_repo.list(offset=offset, limit=limit)
        total = await self.program_repo.count()
        return items, total

    async def update_program(self, program_id: uuid.UUID, data: AcademicProgramUpdate) -> AcademicProgram:
        program = await self.get_program(program_id)
        return await self.program_repo.update(program, data.model_dump(exclude_unset=True))

    async def delete_program(self, program_id: uuid.UUID) -> None:
        program = await self.get_program(program_id)
        await self.program_repo.delete(program)

    # ── Students ───────────────────────────────────────────────────────────────

    async def create(self, data: StudentCreate) -> Student:
        if data.email:
            existing = await self.person_repo.get_by_email(data.email)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Email already registered")
        if await self.student_repo.get_by_code(data.student_code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Student code '{data.student_code}' already in use")

        person = Person(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower() if data.email else None,
            phone=data.phone,
        )
        await self.person_repo.create(person)

        student = Student(
            id=person.id,
            student_code=data.student_code,
            academic_program_id=data.academic_program_id,
            grade_level=data.grade_level,
            status=data.status,
            enrollment_date=data.enrollment_date,
        )
        await self.student_repo.create(student)
        return await self.student_repo.get_with_person(student.id)  # type: ignore[return-value]

    async def get(self, student_id: uuid.UUID) -> Student:
        student = await self.student_repo.get_with_person(student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Student not found")
        return student

    async def list(
        self, *, offset: int = 0, limit: int = 50,
        academic_program_id: uuid.UUID | None = None,
        status=None,
    ) -> tuple[list[Student], int]:
        items = await self.student_repo.list_active(
            offset=offset, limit=limit,
            academic_program_id=academic_program_id, status=status,
        )
        total = await self.student_repo.count_active(
            academic_program_id=academic_program_id, status=status,
        )
        return items, total

    async def update(self, student_id: uuid.UUID, data: StudentUpdate) -> Student:
        student = await self.get(student_id)
        update = data.model_dump(exclude_unset=True)
        person_fields = {k: update.pop(k) for k in ("first_name", "last_name", "email", "phone") if k in update}
        if person_fields:
            await self.person_repo.update(student.person, person_fields)
        if update:
            await self.student_repo.update(student, update)
        await self.db.refresh(student)
        return student

    async def delete(self, student_id: uuid.UUID) -> None:
        student = await self.get(student_id)
        await self.person_repo.soft_delete_cascade(student.person)
