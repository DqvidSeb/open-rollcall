from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.person import Person
from app.models.user import User
from app.repositories.person import PersonRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse, UserCreate, UserUpdate


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.person_repo = PersonRepository(db)

    # ── Auth ───────────────────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_person_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Account disabled")
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError
            user_id = uuid.UUID(payload["sub"])
        except (JWTError, ValueError, KeyError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token")
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # ── User management ────────────────────────────────────────────────────────

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.person_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email already registered")
        person = Person(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower(),
        )
        await self.person_repo.create(person)
        user = User(
            id=person.id,
            hashed_password=hash_password(data.password),
            is_superuser=data.is_superuser,
        )
        return await self.user_repo.create(user)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_with_person(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")
        return user

    async def list_users(self, *, offset: int = 0, limit: int = 50) -> tuple[list[User], int]:
        items = await self.user_repo.list_with_persons(offset=offset, limit=limit)
        total = await self.user_repo.count_active()
        return items, total

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        update = data.model_dump(exclude_unset=True)

        # Separar campos de Person y de User
        person_fields = {k: update.pop(k)
                         for k in ("first_name", "last_name", "email") if k in update}
        if "email" in person_fields:
            person_fields["email"] = person_fields["email"].lower()
        if person_fields:
            await self.person_repo.update(user.person, person_fields)

        # Convertir password → hashed_password
        if "password" in update:
            update["hashed_password"] = hash_password(update.pop("password"))
        if update:
            await self.user_repo.update(user, update)

        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)
        await self.person_repo.soft_delete_cascade(user.person)
