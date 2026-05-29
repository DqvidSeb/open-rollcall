from __future__ import annotations

"""Endpoints de autenticación."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select

from app.core.dependencies import CurrentUserId, DbSession
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenResponse, UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenResponse:
    """Acepta email + password vía form-data (compatible con OAuth2)."""
    service = AuthService(db)
    return await service.login(email=form.username, password=form.password)


@router.post("/refresh", response_model=TokenResponse, summary="Renovar tokens")
async def refresh(body: RefreshRequest, db: DbSession) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh(body.refresh_token)


@router.post(
    "/setup",
    response_model=UserRead,
    status_code=201,
    summary="Crear primer superuser (solo si no existe ninguno)",
)
async def setup_first_superuser(body: UserCreate, db: DbSession) -> UserRead:
    """
    Endpoint de bootstrap — sin autenticación.
    Solo funciona si la tabla 'user' está vacía.
    Se llama una sola vez después del primer despliegue.
    """
    count = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Setup already done. Use /auth/register with a superuser token.",
        )
    body.is_superuser = True
    service = AuthService(db)
    user = await service.create_user(body)
    from app.repositories.user import UserRepository
    user_with_person = await UserRepository(db).get_with_person(user.id)
    if not user_with_person:
        raise HTTPException(status_code=500, detail="Could not reload user")
    return UserRead.model_validate(user_with_person)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Crear usuario admin (requiere superuser autenticado)",
)
async def register(
    body: UserCreate,
    db: DbSession,
    _: CurrentUserId,
) -> UserRead:
    service = AuthService(db)
    user = await service.create_user(body)
    from app.repositories.user import UserRepository
    user_with_person = await UserRepository(db).get_with_person(user.id)
    if not user_with_person:
        raise HTTPException(status_code=500, detail="Could not reload user")
    return UserRead.model_validate(user_with_person)


@router.get("/me", response_model=UserRead, summary="Datos del usuario actual")
async def me(db: DbSession, current_user_id: CurrentUserId) -> UserRead:
    from app.repositories.user import UserRepository
    user = await UserRepository(db).get_with_person(current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)
