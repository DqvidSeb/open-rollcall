from __future__ import annotations

import uuid
from datetime import date, datetime
from sqlalchemy import and_, cast, Date, select
from sqlalchemy.orm import joinedload
from app.models.attendance_log import AttendanceLog, EventType
from app.models.employee import Employee
from app.models.person import Person
from app.models.student import Student
from app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[AttendanceLog]):
    model = AttendanceLog

    async def get_today_event(self, person_id: uuid.UUID, event_type: EventType) -> AttendanceLog | None:
        result = await self.db.execute(
            select(AttendanceLog)
            .where(
                and_(
                    AttendanceLog.person_id == person_id,
                    AttendanceLog.event_type == event_type,
                    cast(AttendanceLog.event_time, Date) == date.today(),
                )
            )
            .order_by(AttendanceLog.event_time.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_person(self, person_id: uuid.UUID, *, date_from: datetime | None = None,
                              date_to: datetime | None = None, offset: int = 0, limit: int = 50) -> list[AttendanceLog]:
        filters = [AttendanceLog.person_id == person_id]
        if date_from:
            filters.append(AttendanceLog.event_time >= date_from)
        if date_to:
            filters.append(AttendanceLog.event_time <= date_to)
        return await self.list(offset=offset, limit=limit, filters=filters)

    async def count_by_person(self, person_id: uuid.UUID, date_from: datetime | None = None,
                               date_to: datetime | None = None) -> int:
        filters = [AttendanceLog.person_id == person_id]
        if date_from:
            filters.append(AttendanceLog.event_time >= date_from)
        if date_to:
            filters.append(AttendanceLog.event_time <= date_to)
        return await self.count(filters=filters)

    async def list_by_date(self, target_date: date, *, offset: int = 0, limit: int = 500) -> list[AttendanceLog]:
        return await self.list(offset=offset, limit=limit,
                               filters=[cast(AttendanceLog.event_time, Date) == target_date])

    async def list_all(self, *, offset: int = 0, limit: int = 50) -> list[AttendanceLog]:
        """Lista todos los registros de asistencia, mas recientes primero,
        con la persona y sus datos de especializacion precargados."""
        result = await self.db.execute(
            select(AttendanceLog)
            .options(
                joinedload(AttendanceLog.person).joinedload(Person.employee).joinedload(Employee.department),
                joinedload(AttendanceLog.person).joinedload(Person.employee).joinedload(Employee.position),
                joinedload(AttendanceLog.person).joinedload(Person.student).joinedload(Student.academic_program),
            )
            .order_by(AttendanceLog.event_time.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def count_all(self) -> int:
        return await self.count()
