from __future__ import annotations

import uuid
import logging
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance_log import AttendanceLog, AttendanceMethod, EventType
from app.models.schedule import Schedule
from app.repositories.attendance import AttendanceRepository
from app.repositories.person import PersonRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.attendance import AttendanceManualCreate, AttendanceSummary
from app.schemas.face import FaceVerifyResponse

logger = logging.getLogger(__name__)


def _classify_event(now_local: datetime, schedule: Schedule) -> EventType | None:
    """
    Determina el tipo de evento (check_in / check_out) según la hora local
    del nodo de cámara y las ventanas del schedule activo.

    Retorna None si la hora actual cae fuera de ambas ventanas (horario bloqueado).

    Lógica:
      · Si la hora está dentro de la ventana de check-in  → CHECK_IN
      · Si la hora está dentro de la ventana de check-out → CHECK_OUT
      · En caso de superposición (configuración errónea), check-in tiene prioridad.
    """
    t = now_local.time()
    if schedule.check_in_start <= t < schedule.check_in_end:
        return EventType.CHECK_IN
    if schedule.checkout_start <= t < schedule.checkout_end:
        return EventType.CHECK_OUT
    return None


class AttendanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.att_repo = AttendanceRepository(db)
        self.person_repo = PersonRepository(db)
        self.sch_repo = ScheduleRepository(db)

    async def _get_active_schedule(self) -> Schedule:
        """
        Carga el schedule activo desde BD.
        Si no existe, retorna uno por defecto en memoria (no persistido)
        para que el sistema nunca quede bloqueado por falta de configuración.
        """
        from app.services.schedule_service import ScheduleService
        svc = ScheduleService(self.sch_repo.db)
        return await svc.get_active()

    async def record_from_recognition(self, verify_result: FaceVerifyResponse,
                                       snapshot_url: str | None = None) -> AttendanceLog:
        """
        Registra asistencia a partir del resultado de reconocimiento facial.

        Validaciones:
          1. La persona debe ser reconocida.
          2. No debe haber completado ya su entrada y salida del día.
          3. La hora actual (en la TZ del schedule activo) debe caer dentro
             de la ventana de check-in o check-out configurada.
        """
        # ── 1. Verificar reconocimiento ───────────────────────────────────────
        if not verify_result.recognized or not verify_result.person_id:
            detail = verify_result.message or "Cannot record attendance for unrecognized person"
            raise HTTPException(status_code=422, detail=detail)

        pid = verify_result.person_id

        # ── 2. Verificar eventos del día ──────────────────────────────────────
        existing_in = await self.att_repo.get_today_event(pid, EventType.CHECK_IN)
        existing_out = await self.att_repo.get_today_event(pid, EventType.CHECK_OUT)

        if existing_in and existing_out:
            last = existing_out.event_time.isoformat() if existing_out.event_time else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Ya completó entrada y salida hoy. "
                    f"Último evento registrado: {last}"
                ),
            )

        # ── 3. Validar ventana horaria con el schedule activo ─────────────────
        schedule = await self._get_active_schedule()
        tz = ZoneInfo(schedule.timezone)
        now_local = datetime.now(tz)

        expected_type = EventType.CHECK_IN if not existing_in else EventType.CHECK_OUT
        event_type = _classify_event(now_local, schedule)

        if event_type is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Registro no permitido fuera del horario configurado. "
                    f"Hora actual ({schedule.timezone}): {now_local.strftime('%H:%M:%S')}. "
                    f"Ventana check-in: {schedule.check_in_start}–{schedule.check_in_end}. "
                    f"Ventana check-out: {schedule.checkout_start}–{schedule.checkout_end}."
                ),
            )

        # Si la ventana activa no coincide con lo esperado, usar la lógica
        # del servidor (existencia de eventos previos) como desempate.
        # Ejemplo: llega tarde y la ventana checkin ya cerró, pero no había marcado;
        # en ese caso se acepta la ventana de checkout si está abierta y viceversa.
        resolved_type = event_type if event_type == expected_type else expected_type

        log = AttendanceLog(
            person_id=pid,
            event_type=resolved_type,
            method=AttendanceMethod.FACE_RECOGNITION,
            event_time=datetime.now(UTC),
            confidence=verify_result.confidence,
            snapshot_url=snapshot_url,
        )
        return await self.att_repo.create(log)

    async def record_manual(self, data: AttendanceManualCreate, recorded_by: uuid.UUID) -> AttendanceLog:
        person = await self.person_repo.get_attendee(data.person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        log = AttendanceLog(
            person_id=data.person_id,
            event_type=data.event_type,
            method=AttendanceMethod.MANUAL,
            event_time=data.event_time or datetime.now(UTC),
            recorded_by=recorded_by,
            notes=data.notes,
        )
        return await self.att_repo.create(log)

    async def get_daily_summary(self, target_date: date) -> list[AttendanceSummary]:
        from app.services.face_service import _person_type_and_code

        records = await self.att_repo.list_by_date(target_date)
        by_person: dict[uuid.UUID, dict] = {}
        for att in records:
            pid = att.person_id
            if pid not in by_person:
                by_person[pid] = {"check_in": None, "check_out": None}
            if att.event_type == EventType.CHECK_IN and not by_person[pid]["check_in"]:
                by_person[pid]["check_in"] = att.event_time
            elif att.event_type == EventType.CHECK_OUT:
                by_person[pid]["check_out"] = att.event_time

        summaries = []
        for pid, times in by_person.items():
            person = await self.person_repo.get_attendee(pid)
            if not person:
                continue
            person_type, code = _person_type_and_code(person)
            total_hours = None
            if times["check_in"] and times["check_out"]:
                total_hours = round((times["check_out"] - times["check_in"]).total_seconds() / 3600, 2)
            summaries.append(AttendanceSummary(
                person_id=pid,
                person_type=person_type,
                full_name=person.full_name,
                code=code or "",
                date=target_date.isoformat(),
                check_in_time=times["check_in"],
                check_out_time=times["check_out"],
                total_hours=total_hours,
            ))
        return summaries

    async def list_by_person(self, person_id: uuid.UUID, *, date_from=None,
                              date_to=None, offset=0, limit=50):
        items = await self.att_repo.list_by_person(
            person_id, date_from=date_from, date_to=date_to, offset=offset, limit=limit)
        total = await self.att_repo.count_by_person(
            person_id, date_from=date_from, date_to=date_to)
        return items, total
