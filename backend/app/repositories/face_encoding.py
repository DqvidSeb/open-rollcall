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
        top_k: int = 5,
        distance_threshold: float = 0.40,
    ) -> list[tuple[FaceEncoding, float]]:
        """Búsqueda por distancia coseno usando pgvector (<=>)."""
        query_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        stmt = text(
            """
            SELECT fe.id, fe.embedding <=> CAST(:query AS vector) AS distance
            FROM face_encoding fe
            WHERE fe.embedding <=> CAST(:query AS vector) < :threshold
            ORDER BY distance ASC
            LIMIT :top_k
            """
        )
        rows = await self.db.execute(
            stmt, {"query": query_str, "threshold": distance_threshold, "top_k": top_k}
        )
        out: list[tuple[FaceEncoding, float]] = []
        for row in rows.fetchall():
            enc = await self.db.get(FaceEncoding, row.id)
            if enc:
                out.append((enc, float(row.distance)))
        return out
