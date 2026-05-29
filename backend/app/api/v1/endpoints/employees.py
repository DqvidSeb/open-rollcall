from __future__ import annotations

"""
Endpoints de empleados, departamentos y posiciones.
"""

import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.employee import (
    DepartmentCreate, DepartmentRead, DepartmentUpdate, PaginatedDepartments,
    EmployeeCreate, EmployeeRead, EmployeeUpdate, PaginatedEmployees,
    PositionCreate, PositionRead, PositionUpdate, PaginatedPositions,
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


# ══════════════════════════════════════════════════════════════════════════════
# DEPARTMENTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/departments",
    response_model=DepartmentRead,
    status_code=201,
    summary="Crear departamento",
)
async def create_department(
    body: DepartmentCreate,
    db: DbSession,
    _: CurrentUserId,
) -> DepartmentRead:
    svc = EmployeeService(db)
    return DepartmentRead.model_validate(await svc.create_department(body))


@router.get(
    "/departments",
    response_model=PaginatedDepartments,
    summary="Listar departamentos (paginado)",
)
async def list_departments(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
) -> PaginatedDepartments:
    svc = EmployeeService(db)
    items, total = await svc.list_departments(offset=offset, limit=limit)
    return PaginatedDepartments(
        items=[DepartmentRead.model_validate(d) for d in items],
        total=total, offset=offset, limit=limit,
    )


@router.get(
    "/departments/{department_id}",
    response_model=DepartmentRead,
    summary="Obtener departamento por ID",
)
async def get_department(
    department_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> DepartmentRead:
    svc = EmployeeService(db)
    return DepartmentRead.model_validate(await svc.get_department(department_id))


@router.patch(
    "/departments/{department_id}",
    response_model=DepartmentRead,
    summary="Actualizar departamento",
)
async def update_department(
    department_id: uuid.UUID,
    body: DepartmentUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> DepartmentRead:
    svc = EmployeeService(db)
    return DepartmentRead.model_validate(await svc.update_department(department_id, body))


@router.delete(
    "/departments/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar departamento",
)
async def delete_department(
    department_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = EmployeeService(db)
    await svc.delete_department(department_id)


# ══════════════════════════════════════════════════════════════════════════════
# POSITIONS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/positions",
    response_model=PositionRead,
    status_code=201,
    summary="Crear posición/cargo",
)
async def create_position(
    body: PositionCreate,
    db: DbSession,
    _: CurrentUserId,
) -> PositionRead:
    svc = EmployeeService(db)
    return PositionRead.model_validate(await svc.create_position(body))


@router.get(
    "/positions",
    response_model=PaginatedPositions,
    summary="Listar posiciones/cargos (paginado)",
)
async def list_positions(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
) -> PaginatedPositions:
    svc = EmployeeService(db)
    items, total = await svc.list_positions(offset=offset, limit=limit)
    return PaginatedPositions(
        items=[PositionRead.model_validate(p) for p in items],
        total=total, offset=offset, limit=limit,
    )


@router.get(
    "/positions/{position_id}",
    response_model=PositionRead,
    summary="Obtener posición/cargo por ID",
)
async def get_position(
    position_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> PositionRead:
    svc = EmployeeService(db)
    return PositionRead.model_validate(await svc.get_position(position_id))


@router.patch(
    "/positions/{position_id}",
    response_model=PositionRead,
    summary="Actualizar posición/cargo",
)
async def update_position(
    position_id: uuid.UUID,
    body: PositionUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> PositionRead:
    svc = EmployeeService(db)
    return PositionRead.model_validate(await svc.update_position(position_id, body))


@router.delete(
    "/positions/{position_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar posición/cargo",
)
async def delete_position(
    position_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = EmployeeService(db)
    await svc.delete_position(position_id)


# ══════════════════════════════════════════════════════════════════════════════
# EMPLOYEES
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=EmployeeRead,
    status_code=201,
    summary="Crear empleado",
)
async def create_employee(
    body: EmployeeCreate,
    db: DbSession,
    _: CurrentUserId,
) -> EmployeeRead:
    svc = EmployeeService(db)
    return _emp_read(await svc.create(body))


@router.get(
    "",
    response_model=PaginatedEmployees,
    summary="Listar empleados (paginado)",
)
async def list_employees(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
    department_id: uuid.UUID | None = Query(default=None, description="Filtrar por departamento"),
    emp_status: str | None = Query(default=None, alias="status", description="active | inactive | on_leave"),
) -> PaginatedEmployees:
    from app.models.employee import EmployeeStatus
    svc = EmployeeService(db)
    parsed_status = EmployeeStatus(emp_status) if emp_status else None
    items, total = await svc.list(
        offset=offset, limit=limit,
        department_id=department_id, status=parsed_status,
    )
    return PaginatedEmployees(
        items=[_emp_read(e) for e in items],
        total=total, offset=offset, limit=limit,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Obtener empleado por ID",
)
async def get_employee(
    employee_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> EmployeeRead:
    svc = EmployeeService(db)
    return _emp_read(await svc.get(employee_id))


@router.patch(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Actualizar empleado",
)
async def update_employee(
    employee_id: uuid.UUID,
    body: EmployeeUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> EmployeeRead:
    svc = EmployeeService(db)
    return _emp_read(await svc.update(employee_id, body))


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar empleado (soft delete)",
)
async def delete_employee(
    employee_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = EmployeeService(db)
    await svc.delete(employee_id)


# Helper
def _emp_read(emp) -> EmployeeRead:
    return EmployeeRead(
        id=emp.id,
        full_name=emp.person.full_name,
        email=emp.person.email,
        phone=emp.person.phone,
        employee_code=emp.employee_code,
        department_id=emp.department_id,
        position_id=emp.position_id,
        department_name=emp.department.name if emp.department else None,
        position_name=emp.position.name if emp.position else None,
        status=emp.status,
        hire_date=emp.hire_date,
        is_enrolled=bool(emp.face_encodings),
        created_at=emp.created_at,
    )
