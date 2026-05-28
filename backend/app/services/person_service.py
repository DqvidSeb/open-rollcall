from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person
from app.repositories.person import PersonRepository
from app.schemas.person import PersonCreate, PersonUpdate


class PersonService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PersonRepository(db)

    async def create(self, data: PersonCreate) -> Person:
        if data.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Email already registered")
        person = Person(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower() if data.email else None,
            phone=data.phone,
        )
        return await self.repo.create(person)

    async def get(self, person_id: uuid.UUID) -> Person:
        person = await self.repo.get_active(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Person not found")
        return person

    async def list(self, *, offset: int = 0, limit: int = 50) -> tuple[list[Person], int]:
        filters = [Person.deleted_at.is_(None)]
        persons = await self.repo.list(offset=offset, limit=limit, filters=filters)
        total = await self.repo.count(filters=filters)
        return persons, total

    async def update(self, person_id: uuid.UUID, data: PersonUpdate) -> Person:
        person = await self.get(person_id)
        return await self.repo.update(person, data.model_dump(exclude_unset=True))

    async def delete(self, person_id: uuid.UUID) -> None:
        """
        Soft delete en cascada:
        Person → Employee (si existe) → User (si existe)
        Todos reciben deleted_at = now().
        """
        person = await self.repo.get_active(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Person not found")
        await self.repo.soft_delete_cascade(person)
