from __future__ import annotations

import base64
import io
import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.face_encoding import FaceEncoding
from app.repositories.employee import EmployeeRepository
from app.repositories.face_encoding import FaceEncodingRepository
from app.schemas.face import FaceVerifyResponse

logger = logging.getLogger(__name__)
settings = get_settings()


def _require_deepface():
    """
    Lazy import de DeepFace.

    TensorFlow 2.16+ usa Keras 3 por defecto. RetinaFace/DeepFace pueden requerir
    tf-keras para compatibilidad con Keras 2, por eso se fuerza legacy Keras antes
    de importar DeepFace.
    """
    try:
        import os  # noqa: PLC0415

        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

        from deepface import DeepFace  # noqa: PLC0415

        return DeepFace

    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Face recognition engine not available. "
                "Install dependencies with: "
                "pip install deepface tensorflow tf-keras opencv-python-headless Pillow"
            ),
        ) from exc

    except Exception as exc:
        logger.exception("DeepFace import error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Face recognition engine failed to load. "
                "Check TensorFlow/Keras compatibility. "
                "Recommended fix: pip install tf-keras"
            ),
        ) from exc


def _b64_to_numpy(b64: str):
    """Decode a base64 image string to a numpy array (RGB)."""
    try:
        import numpy as np  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image processing libraries not available. Install: pip install Pillow numpy",
        )
    try:
        img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
        return np.array(img)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid image: {exc}")


class FaceService:
    def __init__(self, db: AsyncSession) -> None:
        self.enc_repo = FaceEncodingRepository(db)
        self.emp_repo = EmployeeRepository(db)

    def _extract_embedding(self, img) -> list[float]:
        DeepFace = _require_deepface()
        try:
            result = DeepFace.represent(
                img_path=img,
                model_name=settings.FACE_MODEL_NAME,
                detector_backend=settings.FACE_DETECTOR_BACKEND,
                enforce_detection=settings.FACE_ENFORCE_DETECTION,
                align=True,
            )
            if not result:
                raise ValueError("No face detected")
            return result[0]["embedding"]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("DeepFace error: %s", exc)
            raise HTTPException(status_code=500, detail="Feature extraction failed")

    async def enroll(self, employee_id: uuid.UUID, images_b64: list[str]) -> int:
        emp = await self.emp_repo.get_with_person(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        embeddings = [self._extract_embedding(_b64_to_numpy(img)) for img in images_b64]
        await self.enc_repo.delete_by_employee(employee_id)

        for idx, emb in enumerate(embeddings):
            enc = FaceEncoding(
                employee_id=employee_id,
                embedding=emb,
                sample_index=idx,
                model_name=settings.FACE_MODEL_NAME,
                is_primary=(idx == 0),
            )
            await self.enc_repo.create(enc)

        logger.info("Enrolled %d samples for employee_id=%s", len(embeddings), employee_id)
        return len(embeddings)

    async def verify(self, image_b64: str) -> FaceVerifyResponse:
        emb = self._extract_embedding(_b64_to_numpy(image_b64))
        matches = await self.enc_repo.find_nearest(
            query_embedding=emb,
            top_k=5,
            distance_threshold=settings.FACE_DISTANCE_THRESHOLD,
        )
        if not matches:
            return FaceVerifyResponse(recognized=False, message="No matching person found")

        best_enc, best_distance = matches[0]
        emp = await self.emp_repo.get_with_person(best_enc.employee_id)
        if not emp:
            return FaceVerifyResponse(
                recognized=False,
                message="Matched encoding belongs to a deleted employee",
            )

        confidence = round(1.0 - (best_distance / 2.0), 4)
        return FaceVerifyResponse(
            recognized=True,
            employee_id=emp.id,
            full_name=emp.person.full_name,
            employee_code=emp.employee_code,
            confidence=confidence,
            message="Person recognized successfully",
        )

    async def delete_encodings(self, employee_id: uuid.UUID) -> None:
        await self.enc_repo.delete_by_employee(employee_id)
