from __future__ import annotations

"""Endpoints de gestión de usuarios administradores."""

import uuid

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.auth import PaginatedUsers, UserCreate, UserRead, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=201,
    summary="Crear usuario administrador",
)
async def create_user(
    body: UserCreate,
    db: DbSession,
    _: CurrentUserId,
) -> UserRead:
    svc = AuthService(db)
    user = await svc.create_user(body)
    from app.repositories.user import UserRepository
    return UserRead.model_validate(await UserRepository(db).get_with_person(user.id))


@router.get(
    "",
    response_model=PaginatedUsers,
    summary="Listar usuarios (paginado)",
)
async def list_users(
    db: DbSession,
    _: CurrentUserId,
    offset: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
) -> PaginatedUsers:
    svc = AuthService(db)
    items, total = await svc.list_users(offset=offset, limit=limit)
    return PaginatedUsers(
        items=[UserRead.model_validate(u) for u in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/me",
    response_model=UserRead,
    summary="Datos del usuario autenticado",
)
async def me(
    db: DbSession,
    current_user_id: CurrentUserId,
) -> UserRead:
    svc = AuthService(db)
    return UserRead.model_validate(await svc.get_user(current_user_id))


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Obtener usuario por ID",
)
async def get_user(
    user_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> UserRead:
    svc = AuthService(db)
    return UserRead.model_validate(await svc.get_user(user_id))


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Actualizar usuario",
)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    db: DbSession,
    _: CurrentUserId,
) -> UserRead:
    svc = AuthService(db)
    user = await svc.update_user(user_id, body)
    from app.repositories.user import UserRepository
    return UserRead.model_validate(await UserRepository(db).get_with_person(user.id))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario (soft delete)",
)
async def delete_user(
    user_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    svc = AuthService(db)
    await svc.delete_user(user_id)
