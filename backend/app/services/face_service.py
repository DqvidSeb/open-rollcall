from __future__ import annotations

import base64
import io
import logging
import math
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.face_encoding import FaceEncoding
from app.repositories.employee import EmployeeRepository
from app.repositories.face_encoding import FaceEncodingRepository
from app.schemas.face import FaceStatusResponse, FaceVerifyResponse

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
        # Si el detector es "skip" no hay que forzar deteccion: el cliente nos
        # mandó la cara ya recortada y alineada. Igual evitamos re-alinear,
        # porque ya viene alineada por landmarks de YuNet/MediaPipe en el
        # cliente -> ahorra ~50ms adicionales por llamada.
        detector_backend = settings.FACE_DETECTOR_BACKEND
        is_skip = detector_backend.lower() == "skip"
        enforce_detection = False if is_skip else settings.FACE_ENFORCE_DETECTION
        align = not is_skip
        try:
            result = DeepFace.represent(
                img_path=img,
                model_name=settings.FACE_MODEL_NAME,
                detector_backend=detector_backend,
                enforce_detection=enforce_detection,
                align=align,
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
        """
        Pipeline:
          1. Extrae el embedding de la imagen recibida.
          2. Trae los top_k vecinos mas cercanos SIN filtrar por threshold
             (para poder reportar la distancia real aun cuando no haya match).
          3. Vota por empleado: el ganador es quien tiene mas muestras dentro
             del threshold. En empate, gana el de menor distancia minima.
          4. Si nadie supera el threshold, devuelve `recognized=False` pero con
             la distancia y nombre del mas cercano -> diagnostico in situ.
        """
        emb = self._extract_embedding(_b64_to_numpy(image_b64))

        # Sanity check de la dimension del embedding antes de tirarlo a
        # pgvector. ArcFace debe devolver 512. Si por alguna razon llega algo
        # distinto pgvector lanza un error muy feo; preferimos un mensaje
        # claro al cliente.
        if len(emb) != 512:
            logger.error(
                "verify: embedding dim=%d (expected 512) — DeepFace returned wrong size",
                len(emb),
            )
            return FaceVerifyResponse(
                recognized=False,
                message=f"Embedding dim {len(emb)} != 512. Modelo mal configurado.",
            )

        # Validacion NaN/Inf: pgvector no lanza error con vectores NaN pero
        # devuelve 0 filas silenciosamente. Detectamos esto antes de la query
        # para dar un mensaje util al operador.
        bad_values = [v for v in emb if not math.isfinite(v)]
        if bad_values:
            logger.error(
                "verify: embedding contains %d NaN/Inf values — frame descartado",
                len(bad_values),
            )
            return FaceVerifyResponse(
                recognized=False,
                message="Frame descartado: embedding invalido (NaN/Inf). Intenta de nuevo.",
            )

        # Conteo total como ground truth. Esto distingue "tabla vacia" de
        # "query devolvio 0 filas por algun otro motivo".
        total = await self.enc_repo.count()
        logger.info("verify: face_encoding total rows=%d", total)

        # Traemos top-10 SIN filtrar por threshold para diagnostico.
        matches = await self.enc_repo.find_nearest(
            query_embedding=emb,
            top_k=10,
            distance_threshold=None,
        )

        if not matches:
            if total == 0:
                logger.info("verify: face_encoding table is empty")
                return FaceVerifyResponse(
                    recognized=False,
                    message="No hay rostros enrolados en el sistema",
                )
            logger.error(
                "verify: find_nearest returned 0 rows despite %d encodings in DB", total
            )
            return FaceVerifyResponse(
                recognized=False,
                message=(
                    f"find_nearest devolvio 0 filas (hay {total} encodings en DB). "
                    "Revisa logs del servidor."
                ),
            )

        # Log de los top-3 para diagnostico.
        for i, (enc, dist) in enumerate(matches[:3]):
            logger.info(
                "verify: top%d employee_id=%s dist=%.4f",
                i + 1, enc.employee_id, dist,
            )

        threshold = settings.FACE_DISTANCE_THRESHOLD

        # Voto por empleado: agrupa las muestras bajo threshold y elige al que
        # mas "votos" tenga; en empate por menor distancia minima.
        per_emp_min: dict[uuid.UUID, float] = {}
        per_emp_votes: dict[uuid.UUID, int] = {}
        for enc, dist in matches:
            if dist < per_emp_min.get(enc.employee_id, float("inf")):
                per_emp_min[enc.employee_id] = dist
            if dist < threshold:
                per_emp_votes[enc.employee_id] = per_emp_votes.get(enc.employee_id, 0) + 1

        absolute_best_enc, absolute_best_dist = matches[0]
        absolute_best_conf = round(max(0.0, 1.0 - (absolute_best_dist / 2.0)), 4)

        if not per_emp_votes:
            # Ningun encoding paso el threshold. Devolvemos la distancia del
            # mas cercano para que el operador sepa que tan cerca esta.
            nearest_emp = await self.emp_repo.get_with_person(
                absolute_best_enc.employee_id
            )
            nearest_name = (
                nearest_emp.person.full_name if nearest_emp else "(empleado eliminado)"
            )
            logger.info(
                "verify: no match within threshold=%.2f. Nearest=%s dist=%.4f",
                threshold, nearest_name, absolute_best_dist,
            )
            return FaceVerifyResponse(
                recognized=False,
                confidence=absolute_best_conf,
                message=(
                    f"Nearest: {nearest_name} dist={absolute_best_dist:.4f} "
                    f"(threshold={threshold:.2f})"
                ),
            )

        # Ganador: mas votos -> en empate, menor distancia minima.
        winner_id = max(
            per_emp_votes.keys(),
            key=lambda eid: (per_emp_votes[eid], -per_emp_min[eid]),
        )
        winner_dist = per_emp_min[winner_id]
        winner_votes = per_emp_votes[winner_id]

        emp = await self.emp_repo.get_with_person(winner_id)
        if not emp:
            logger.warning("verify: matched employee_id=%s no longer exists", winner_id)
            return FaceVerifyResponse(
                recognized=False,
                confidence=absolute_best_conf,
                message="Matched encoding belongs to a deleted employee",
            )

        confidence = round(max(0.0, 1.0 - (winner_dist / 2.0)), 4)
        logger.info(
            "verify: match %s code=%s dist=%.4f votes=%d/10 conf=%.4f",
            emp.person.full_name, emp.employee_code,
            winner_dist, winner_votes, confidence,
        )
        return FaceVerifyResponse(
            recognized=True,
            employee_id=emp.id,
            full_name=emp.person.full_name,
            employee_code=emp.employee_code,
            confidence=confidence,
            message=f"Recognized ({winner_votes}/10 close samples, dist={winner_dist:.4f})",
        )

    async def delete_encodings(self, employee_id: uuid.UUID) -> None:
        await self.enc_repo.delete_by_employee(employee_id)

    async def get_status(self, employee_id: uuid.UUID) -> FaceStatusResponse:
        emp = await self.emp_repo.get(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        samples = await self.enc_repo.count_by_employee(employee_id)
        return FaceStatusResponse(
            employee_id=employee_id,
            enrolled=samples > 0,
            samples=samples,
        )
