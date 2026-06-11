from __future__ import annotations

"""
Endpoints de reconocimiento facial.
"""

import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.attendance import AttendanceRead
from app.schemas.face import (
    EnrollBody,
    FaceEnrollResponse,
    FaceStatusResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
)
from app.repositories.person import PersonRepository
from app.services.attendance_service import AttendanceService
from app.services.face_service import FaceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/face", tags=["face-recognition"])


def _safe(fn, default=None):
    """Llama `fn()` y devuelve `default` si lanza cualquier excepcion.
    Solo para enriquecer campos opcionales — nunca para datos criticos.
    """
    try:
        return fn()
    except Exception:  # noqa: BLE001
        return default


def _build_attendance_read(attendance, person) -> AttendanceRead:
    """
    Construye un `AttendanceRead` enriquecido con datos de la persona
    (empleado o estudiante) que generó el evento.

    Si UN campo opcional explota, NO debe tumbar la respuesta. Los
    unicos campos obligatorios son los del `attendance` (id, event_type, etc.)
    """
    employee = _safe(lambda: person.employee if person else None)
    student = _safe(lambda: person.student if person else None)

    person_type: str | None = None
    code: str | None = None
    if employee is not None:
        person_type = "employee"
        code = _safe(lambda: employee.employee_code)
    elif student is not None:
        person_type = "student"
        code = _safe(lambda: student.student_code)

    def _hire_date_iso():
        hd = _safe(lambda: employee.hire_date if employee else None)
        if hd is None:
            return None
        try:
            return hd.isoformat()
        except Exception:  # noqa: BLE001
            return str(hd)

    def _enrollment_date_iso():
        ed = _safe(lambda: student.enrollment_date if student else None)
        if ed is None:
            return None
        try:
            return ed.isoformat()
        except Exception:  # noqa: BLE001
            return str(ed)

    def _employee_status_value():
        st = _safe(lambda: employee.status if employee else None)
        if st is None:
            return None
        return getattr(st, "value", None) or str(st)

    return AttendanceRead(
        id=attendance.id,
        event_type=attendance.event_type,
        method=attendance.method,
        event_time=attendance.event_time,
        confidence=_safe(lambda: attendance.confidence),
        notes=_safe(lambda: attendance.notes),
        person_id=attendance.person_id,
        person_type=person_type,
        code=code,
        full_name=_safe(lambda: person.full_name if person else None),
        first_name=_safe(lambda: person.first_name if person else None),
        last_name=_safe(lambda: person.last_name if person else None),
        email=_safe(lambda: person.email if person else None),
        phone=_safe(lambda: person.phone if person else None),
        department=_safe(lambda: employee.department.name if employee and employee.department else None),
        position=_safe(lambda: employee.position.name if employee and employee.position else None),
        status=_employee_status_value(),
        hire_date=_hire_date_iso(),
        academic_program=_safe(
            lambda: student.academic_program.name if student and student.academic_program else None
        ),
        grade_level=_safe(lambda: student.grade_level if student else None),
        enrollment_date=_enrollment_date_iso(),
    )


@router.post(
    "/enroll/{person_id}",
    response_model=FaceEnrollResponse,
    status_code=201,
    summary="Registrar rostro de un empleado o estudiante",
)
async def enroll_face(
    person_id: uuid.UUID,
    body: EnrollBody,
    db: DbSession,
    _: CurrentUserId,
) -> FaceEnrollResponse:
    """
    Recibe entre 1 y N imágenes base64 del rostro de la persona (empleado o
    estudiante). Extrae embeddings con DeepFace (ArcFace) y los guarda en
    PostgreSQL. Elimina encodings previos antes de guardar los nuevos.
    """
    service = FaceService(db)
    samples = await service.enroll(
        person_id, body.images_base64, pre_cropped=body.pre_cropped
    )
    return FaceEnrollResponse(
        person_id=person_id,
        samples_captured=samples,
        message=f"Face enrolled successfully with {samples} sample(s)",
    )


@router.post(
    "/verify",
    response_model=FaceVerifyResponse,
    summary="Reconocer un rostro (sin marcar asistencia)",
)
async def verify_face(
    body: FaceVerifyRequest,
    db: DbSession,
    _: CurrentUserId,
) -> FaceVerifyResponse:
    """Solo verifica — no registra asistencia. Hecho para previsualizar."""
    service = FaceService(db)
    return await service.verify(body.image_base64, pre_cropped=body.pre_cropped)


@router.post(
    "/check-in",
    response_model=AttendanceRead,
    status_code=201,
    summary="Reconocer rostro y registrar asistencia",
)
async def check_in(
    body: FaceVerifyRequest,
    db: DbSession,
    _: CurrentUserId,
) -> AttendanceRead:
    """
    Pipeline completo:
      1. Extrae embedding del frame recibido.
      2. Busca a la persona (empleado o estudiante) en la DB por similitud coseno.
      3. Registra check_in o check_out según corresponda.
    """
    face_svc = FaceService(db)
    att_svc = AttendanceService(db)
    person_repo = PersonRepository(db)

    # Envuelto cada paso para que cualquier excepcion inesperada salga al
    # log del servidor con contexto y se convierta en un 500 con detalle
    # legible para el cliente (en vez del HTML genérico de FastAPI).
    try:
        verify_result = await face_svc.verify(
            body.image_base64, pre_cropped=body.pre_cropped
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("check_in: face_svc.verify crashed")
        raise HTTPException(status_code=500, detail=f"verify failed: {exc}") from exc

    try:
        attendance = await att_svc.record_from_recognition(verify_result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("check_in: record_from_recognition crashed")
        raise HTTPException(
            status_code=500, detail=f"record_from_recognition failed: {exc}"
        ) from exc

    try:
        person = await person_repo.get_attendee(attendance.person_id)
    except Exception:  # noqa: BLE001
        logger.exception("check_in: person_repo.get_attendee crashed")
        person = None  # construimos la respuesta sin enriquecimiento

    try:
        return _build_attendance_read(attendance, person)
    except Exception as exc:  # noqa: BLE001
        logger.exception("check_in: _build_attendance_read crashed")
        raise HTTPException(
            status_code=500, detail=f"response build failed: {exc}"
        ) from exc


@router.get(
    "/status/{person_id}",
    response_model=FaceStatusResponse,
    summary="Consultar si una persona tiene rostro registrado",
)
async def get_face_status(
    person_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> FaceStatusResponse:
    service = FaceService(db)
    return await service.get_status(person_id)


@router.delete(
    "/encodings/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar todos los encodings de una persona",
)
async def delete_encodings(
    person_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    service = FaceService(db)
    await service.delete_encodings(person_id)
