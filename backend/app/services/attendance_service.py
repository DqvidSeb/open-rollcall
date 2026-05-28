from __future__ import annotations

import uuid
import logging
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance_log import AttendanceLog, AttendanceMethod, EventType
from app.repositories.attendance import AttendanceRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.attendance import AttendanceManualCreate, AttendanceSummary
from app.schemas.face import FaceVerifyResponse

logger = logging.getLogger(__name__)


class AttendanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.att_repo = AttendanceRepository(db)
        self.emp_repo = EmployeeRepository(db)

    async def record_from_recognition(self, verify_result: FaceVerifyResponse,
                                       snapshot_url: str | None = None) -> AttendanceLog:
        # Si el motor de reconocimiento no encontro match, propagamos al cliente
        # el mismo `message` que produjo verify (incluye distancia y nombre del
        # mas cercano). Esto reemplaza el genérico "unrecognized person" por
        # algo accionable: "Nearest: Maria Fernanda dist=0.6231 (threshold=0.55)".
        if not verify_result.recognized or not verify_result.employee_id:
            detail = verify_result.message or "Cannot record attendance for unrecognized person"
            raise HTTPException(status_code=422, detail=detail)

        eid = verify_result.employee_id
        existing_in = await self.att_repo.get_today_event(eid, EventType.CHECK_IN)
        existing_out = await self.att_repo.get_today_event(eid, EventType.CHECK_OUT)

        if existing_in and existing_out:
            # 409 con detalle claro y hora del ultimo check para diagnostico.
            last = existing_out.event_time.isoformat() if existing_out.event_time else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Ya completo entrada y salida hoy. "
                    f"Ultimo evento registrado: {last}"
                ),
            )

        log = AttendanceLog(
            employee_id=eid,
            event_type=EventType.CHECK_IN if not existing_in else EventType.CHECK_OUT,
            method=AttendanceMethod.FACE_RECOGNITION,
            event_time=datetime.now(UTC),
            confidence=verify_result.confidence,
            snapshot_url=snapshot_url,
        )
        return await self.att_repo.create(log)

    async def record_manual(self, data: AttendanceManualCreate, recorded_by: uuid.UUID) -> AttendanceLog:
        emp = await self.emp_repo.get_with_person(data.employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        log = AttendanceLog(
            employee_id=data.employee_id,
            event_type=data.event_type,
            method=AttendanceMethod.MANUAL,
            event_time=data.event_time or datetime.now(UTC),
            recorded_by=recorded_by,
            notes=data.notes,
        )
        return await self.att_repo.create(log)

    async def get_daily_summary(self, target_date: date) -> list[AttendanceSummary]:
        records = await self.att_repo.list_by_date(target_date)
        by_emp: dict[uuid.UUID, dict] = {}
        for att in records:
            eid = att.employee_id
            if eid not in by_emp:
                by_emp[eid] = {"check_in": None, "check_out": None}
            if att.event_type == EventType.CHECK_IN and not by_emp[eid]["check_in"]:
                by_emp[eid]["check_in"] = att.event_time
            elif att.event_type == EventType.CHECK_OUT:
                by_emp[eid]["check_out"] = att.event_time

        summaries = []
        for eid, times in by_emp.items():
            emp = await self.emp_repo.get_with_person(eid)
            if not emp:
                continue
            total_hours = None
            if times["check_in"] and times["check_out"]:
                total_hours = round((times["check_out"] - times["check_in"]).total_seconds() / 3600, 2)
            summaries.append(AttendanceSummary(
                employee_id=eid,
                full_name=emp.person.full_name,
                employee_code=emp.employee_code,
                date=target_date.isoformat(),
                check_in_time=times["check_in"],
                check_out_time=times["check_out"],
                total_hours=total_hours,
            ))
        return summaries

    async def list_by_employee(self, employee_id: uuid.UUID, *, date_from=None,
                                date_to=None, offset=0, limit=50):
        items = await self.att_repo.list_by_employee(
            employee_id, date_from=date_from, date_to=date_to, offset=offset, limit=limit)
        total = await self.att_repo.count_by_employee(
            employee_id, date_from=date_from, date_to=date_to)
        return items, total
