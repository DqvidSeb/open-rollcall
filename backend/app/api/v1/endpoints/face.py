from __future__ import annotations

"""
Endpoints de reconocimiento facial.

POST /face/enroll/{employee_id}    — registrar rostro de un empleado
POST /face/verify                  — reconocer un rostro (sin marcar asistencia)
POST /face/check-in                — reconocer y marcar asistencia automáticamente
DELETE /face/encodings/{employee_id} — eliminar encodings de un empleado
"""

import uuid

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUserId, DbSession
from app.schemas.attendance import AttendanceRead
from app.schemas.face import (
    EnrollBody,
    FaceEnrollResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
)
from app.services.attendance_service import AttendanceService
from app.services.face_service import FaceService

router = APIRouter(prefix="/face", tags=["face-recognition"])


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
    """Solo verifica — no registra asistencia. Útil para previsualizar."""
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

    verify_result = await face_svc.verify(body.image_base64)
    attendance = await att_svc.record_from_recognition(verify_result)
    return AttendanceRead.model_validate(attendance)


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
