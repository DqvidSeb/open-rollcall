from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.person import Person
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    model = Person

    def _active(self):
        return Person.deleted_at.is_(None)

    async def get_active(self, id: uuid.UUID) -> Person | None:
        result = await self.db.execute(
            select(Person)
            .options(joinedload(Person.user), joinedload(Person.employee))
            .where(Person.id == id, self._active())
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Person | None:
        result = await self.db.execute(
            select(Person).where(Person.email == email.lower(), self._active())
        )
        return result.scalar_one_or_none()

    async def soft_delete_cascade(self, person: Person) -> None:
        """
        Soft delete en cascada.

        - Person.deleted_at = now  →  la oculta de TODAS las queries
          (employees y users ya hacen JOIN con person y filtran deleted_at IS NULL)
        - User.is_active = False   →  bloquea login inmediatamente aunque
          el token aún no haya expirado
        - Employee no necesita campo propio: sus repositorios filtran
          por Person.deleted_at, por lo que queda invisible automáticamente.
        """
        now = datetime.now(UTC)
        person.deleted_at = now

        if person.user is not None:
            person.user.is_active = False

        await self.db.flush()
