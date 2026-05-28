from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.person import Person
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_person_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .join(Person, User.id == Person.id)
            .options(joinedload(User.person))
            .where(
                Person.email == email.lower(),
                Person.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_with_person(self, id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(joinedload(User.person))
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def list_with_persons(self, *, offset: int = 0, limit: int = 50) -> list[User]:
        result = await self.db.execute(
            select(User)
            .join(Person, User.id == Person.id)
            .options(joinedload(User.person))
            .where(Person.deleted_at.is_(None))
            .order_by(Person.first_name)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def count_active(self) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(User)
            .join(Person, User.id == Person.id)
            .where(Person.deleted_at.is_(None))
        )
        return result.scalar_one()
