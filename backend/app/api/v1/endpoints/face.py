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
    FaceVerifyRequest,
    FaceVerifyResponse,
)
from app.repositories.employee import EmployeeRepository
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


def _build_attendance_read(attendance, employee) -> AttendanceRead:
    """
    Construye un `AttendanceRead` enriquecido con datos del empleado y la
    persona.

    si UN campo opcional explota, NO debe tumbar la respuesta. Los
    unicos campos obligatorios son los del `attendance` (id, event_type, etc.)
    """
    person = _safe(lambda: employee.person if employee else None)
    department = _safe(lambda: employee.department if employee else None)
    position = _safe(lambda: employee.position if employee else None)

    def _status_value():
        st = _safe(lambda: employee.status if employee else None)
        if st is None:
            return None
        return getattr(st, "value", None) or str(st)

    def _hire_date_iso():
        hd = _safe(lambda: employee.hire_date if employee else None)
        if hd is None:
            return None
        try:
            return hd.isoformat()
        except Exception:  # noqa: BLE001
            return str(hd)

    return AttendanceRead(
        id=attendance.id,
        event_type=attendance.event_type,
        method=attendance.method,
        event_time=attendance.event_time,
        confidence=_safe(lambda: attendance.confidence),
        notes=_safe(lambda: attendance.notes),
        employee_id=attendance.employee_id,
        employee_code=_safe(lambda: employee.employee_code if employee else None),
        full_name=_safe(lambda: person.full_name if person else None),
        first_name=_safe(lambda: person.first_name if person else None),
        last_name=_safe(lambda: person.last_name if person else None),
        email=_safe(lambda: person.email if person else None),
        phone=_safe(lambda: person.phone if person else None),
        department=_safe(lambda: department.name if department else None),
        position=_safe(lambda: position.name if position else None),
        status=_status_value(),
        hire_date=_hire_date_iso(),
    )


@router.post(
    "/enroll/{employee_id}",
    response_model=FaceEnrollResponse,
    status_code=201,
    summary="Registrar rostro de un empleado",
)
async def enroll_face(
    employee_id: uuid.UUID,
    body: EnrollBody,
    db: DbSession,
    _: CurrentUserId,
) -> FaceEnrollResponse:
    """
    Recibe entre 1 y N imágenes base64 del rostro del empleado.
    Extrae embeddings con DeepFace (ArcFace) y los guarda en PostgreSQL.
    Elimina encodings previos antes de guardar los nuevos.
    """
    service = FaceService(db)
    samples = await service.enroll(employee_id, body.images_base64)
    return FaceEnrollResponse(
        employee_id=employee_id,
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
    return await service.verify(body.image_base64)


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
      2. Busca al empleado en la DB por similitud coseno.
      3. Registra check_in o check_out según corresponda.
    """
    face_svc = FaceService(db)
    att_svc = AttendanceService(db)
    emp_repo = EmployeeRepository(db)

    # Envuelto cada paso para que cualquier excepcion inesperada salga al
    # log del servidor con contexto y se convierta en un 500 con detalle
    # legible para el cliente (en vez del HTML genérico de FastAPI).
    try:
        verify_result = await face_svc.verify(body.image_base64)
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
        employee = await emp_repo.get_with_person(attendance.employee_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("check_in: emp_repo.get_with_person crashed")
        employee = None  # construimos la respuesta sin enriquecimiento

    try:
        return _build_attendance_read(attendance, employee)
    except Exception as exc:  # noqa: BLE001
        logger.exception("check_in: _build_attendance_read crashed")
        raise HTTPException(
            status_code=500, detail=f"response build failed: {exc}"
        ) from exc


@router.delete(
    "/encodings/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar todos los encodings de un empleado",
)
async def delete_encodings(
    employee_id: uuid.UUID,
    db: DbSession,
    _: CurrentUserId,
) -> None:
    service = FaceService(db)
    await service.delete_encodings(employee_id)
