from __future__ import annotations

"""Endpoints CRUD de personas."""

import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.person import (
    PaginatedPersons, PersonCreate, PersonListItem, PersonRead, PersonUpdate,
)
from app.services.person_service import PersonService

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonRead, status_code=201, summary="Crear persona")
async def create_person(
    body: PersonCreate, db: DbSession, _: CurrentUserId,
) -> PersonRead:
    svc = PersonService(db)
    return PersonRead.model_validate(await svc.create(body))


@router.get("", response_model=PaginatedPersons, summary="Listar personas (paginado)")
async def list_persons(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
) -> PaginatedPersons:
    svc = PersonService(db)
    persons, total = await svc.list(offset=offset, limit=limit)
    return PaginatedPersons(
        items=[_to_list_item(p) for p in persons],
        total=total, offset=offset, limit=limit,
    )


@router.get("/{person_id}", response_model=PersonRead, summary="Obtener persona por ID")
async def get_person(
    person_id: uuid.UUID, db: DbSession, _: CurrentUserId,
) -> PersonRead:
    svc = PersonService(db)
    return PersonRead.model_validate(await svc.get(person_id))


@router.patch("/{person_id}", response_model=PersonRead, summary="Actualizar persona")
async def update_person(
    person_id: uuid.UUID, body: PersonUpdate, db: DbSession, _: CurrentUserId,
) -> PersonRead:
    svc = PersonService(db)
    return PersonRead.model_validate(await svc.update(person_id, body))


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar persona (soft delete)",
)
async def delete_person(
    person_id: uuid.UUID, db: DbSession, _: CurrentUserId,
) -> None:
    svc = PersonService(db)
    await svc.delete(person_id)


def _to_list_item(person) -> PersonListItem:
    person_type: str | None = None
    code: str | None = None
    group_name: str | None = None
    person_status: str | None = None

    if person.employee is not None:
        person_type = "employee"
        code = person.employee.employee_code
        group_name = person.employee.department.name if person.employee.department else None
        person_status = person.employee.status.value
    elif person.student is not None:
        person_type = "student"
        code = person.student.student_code
        group_name = person.student.academic_program.name if person.student.academic_program else None
        person_status = person.student.status.value

    return PersonListItem(
        id=person.id,
        full_name=person.full_name,
        email=person.email,
        phone=person.phone,
        person_type=person_type,
        code=code,
        group_name=group_name,
        status=person_status,
        created_at=person.created_at,
    )
