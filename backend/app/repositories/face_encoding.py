from __future__ import annotations

import uuid
from sqlalchemy import select, text
from app.models.face_encoding import FaceEncoding
from app.repositories.base import BaseRepository


class FaceEncodingRepository(BaseRepository[FaceEncoding]):
    model = FaceEncoding

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[FaceEncoding]:
        result = await self.db.execute(
            select(FaceEncoding)
            .where(FaceEncoding.employee_id == employee_id)
            .order_by(FaceEncoding.sample_index)
        )
        return list(result.scalars().all())

    async def delete_by_employee(self, employee_id: uuid.UUID) -> None:
        encodings = await self.get_by_employee(employee_id)
        for enc in encodings:
            await self.db.delete(enc)
        await self.db.flush()

    async def find_nearest(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        distance_threshold: float | None = None,
    ) -> list[tuple[FaceEncoding, float]]:
        """
        Búsqueda de los k vecinos más cercanos por distancia coseno (pgvector `<=>`).

        Cambios respecto a la versión anterior:
        - El filtro por threshold es opcional. Cuando es `None` devolvemos los
          top_k absolutos, para que la capa superior pueda reportar la
          distancia real incluso cuando no haya match (clave para diagnostico).
        - `top_k` por defecto es 10, no 5. Si un empleado tiene 5 muestras
          enroladas y traemos solo 5 vecinos, podemos quedarnos sin "ver" otras
          personas y perder informacion para el voto por empleado en la capa de
          servicio.
        - Se castea explicitamente el `top_k` a `int` para evitar el corner case
          donde llegue como `numpy.int64` y SQLAlchemy lo rechace.
        """
        query_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        if distance_threshold is None:
            stmt = text(
                """
                SELECT fe.id,
                       fe.embedding <=> CAST(:query AS vector) AS distance
                FROM face_encoding fe
                ORDER BY distance ASC
                LIMIT :top_k
                """
            )
            params = {"query": query_str, "top_k": int(top_k)}
        else:
            stmt = text(
                """
                SELECT fe.id,
                       fe.embedding <=> CAST(:query AS vector) AS distance
                FROM face_encoding fe
                WHERE fe.embedding <=> CAST(:query AS vector) < :threshold
                ORDER BY distance ASC
                LIMIT :top_k
                """
            )
            params = {
                "query": query_str,
                "threshold": float(distance_threshold),
                "top_k": int(top_k),
            }

        rows = await self.db.execute(stmt, params)
        out: list[tuple[FaceEncoding, float]] = []
        for row in rows.fetchall():
            enc = await self.db.get(FaceEncoding, row.id)
            if enc:
                out.append((enc, float(row.distance)))
        return out
