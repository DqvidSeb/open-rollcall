from __future__ import annotations

import uuid
from datetime import date, datetime
from sqlalchemy import and_, cast, Date, select
from app.models.attendance_log import AttendanceLog, EventType
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
