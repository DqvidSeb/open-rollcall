from __future__ import annotations

"""
Endpoints de estudiantes y programas académicos.
"""

import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.student import (
    AcademicProgramCreate, AcademicProgramRead, AcademicProgramUpdate, PaginatedAcademicPrograms,
    StudentCreate, StudentRead, StudentUpdate, PaginatedStudents,
)
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


# ══════════════════════════════════════════════════════════════════════════════
# ACADEMIC PROGRAMS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/programs",
    response_model=AcademicProgramRead,
    status_code=201,
    summary="Crear programa académico",
)
async def create_program(
    body: AcademicProgramCreate,
    db: DbSession,
    _: CurrentUserId,
) -> AcademicProgramRead:
    svc = StudentService(db)
    return AcademicProgramRead.model_validate(await svc.create_program(body))


@router.get(
    "/programs",
    response_model=PaginatedAcademicPrograms,
    summary="Listar programas académicos (paginado)",
)
async def list_programs(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
) -> PaginatedAcademicPrograms:
    svc = StudentService(db)
    items, total = await svc.list_programs(offset=offset, limit=limit)
    return PaginatedAcademicPrograms(
        items=[AcademicProgramRead.model_validate(p) for p in items],
        total=total, offset=offset, limit=limit,
    )


@router.get(
    "/programs/{program_id}",
    response_model=AcademicProgramRead,
    summary="Obtener programa académico por ID",
)
async def get_program(
    program_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> AcademicProgramRead:
    svc = StudentService(db)
    return AcademicProgramRead.model_validate(await svc.get_program(program_id))


@router.patch(
    "/programs/{program_id}",
    response_model=AcademicProgramRead,
    summary="Actualizar programa académico",
)
async def update_program(
    program_id: uuid.UUID,
    body: AcademicProgramUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> AcademicProgramRead:
    svc = StudentService(db)
    return AcademicProgramRead.model_validate(await svc.update_program(program_id, body))


@router.delete(
    "/programs/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar programa académico",
)
async def delete_program(
    program_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = StudentService(db)
    await svc.delete_program(program_id)


# ══════════════════════════════════════════════════════════════════════════════
# STUDENTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=StudentRead,
    status_code=201,
    summary="Crear estudiante",
)
async def create_student(
    body: StudentCreate,
    db: DbSession,
    _: CurrentUserId,
) -> StudentRead:
    svc = StudentService(db)
    return _student_read(await svc.create(body))


@router.get(
    "",
    response_model=PaginatedStudents,
    summary="Listar estudiantes (paginado)",
)
async def list_students(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
    academic_program_id: uuid.UUID | None = Query(default=None, description="Filtrar por programa académico"),
    student_status: str | None = Query(default=None, alias="status", description="active | inactive | graduated | suspended"),
) -> PaginatedStudents:
    from app.models.student import StudentStatus
    svc = StudentService(db)
    parsed_status = StudentStatus(student_status) if student_status else None
    items, total = await svc.list(
        offset=offset, limit=limit,
        academic_program_id=academic_program_id, status=parsed_status,
    )
    return PaginatedStudents(
        items=[_student_read(s) for s in items],
        total=total, offset=offset, limit=limit,
    )


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    summary="Obtener estudiante por ID",
)
async def get_student(
    student_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> StudentRead:
    svc = StudentService(db)
    return _student_read(await svc.get(student_id))


@router.patch(
    "/{student_id}",
    response_model=StudentRead,
    summary="Actualizar estudiante",
)
async def update_student(
    student_id: uuid.UUID,
    body: StudentUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> StudentRead:
    svc = StudentService(db)
    return _student_read(await svc.update(student_id, body))


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estudiante (soft delete)",
)
async def delete_student(
    student_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = StudentService(db)
    await svc.delete(student_id)


# Helper
def _student_read(student) -> StudentRead:
    return StudentRead(
        id=student.id,
        full_name=student.person.full_name,
        email=student.person.email,
        phone=student.person.phone,
        student_code=student.student_code,
        academic_program_id=student.academic_program_id,
        academic_program_name=student.academic_program.name if student.academic_program else None,
        grade_level=student.grade_level,
        status=student.status,
        enrollment_date=student.enrollment_date,
        created_at=student.created_at,
    )
