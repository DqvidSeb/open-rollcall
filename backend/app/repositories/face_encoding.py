from __future__ import annotations

import uuid
from sqlalchemy import func, select
from app.models.face_encoding import FaceEncoding
from app.repositories.base import BaseRepository


class FaceEncodingRepository(BaseRepository[FaceEncoding]):
    model = FaceEncoding

    async def get_by_person(self, person_id: uuid.UUID) -> list[FaceEncoding]:
        result = await self.db.execute(
            select(FaceEncoding)
            .where(FaceEncoding.person_id == person_id)
            .order_by(FaceEncoding.sample_index)
        )
        return list(result.scalars().all())

    async def count_by_person(self, person_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(FaceEncoding)
            .where(FaceEncoding.person_id == person_id)
        )
        return int(result.scalar_one())

    async def delete_by_person(self, person_id: uuid.UUID) -> None:
        encodings = await self.get_by_person(person_id)
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

        Usa FaceEncoding.embedding.cosine_distance() del comparator de pgvector,
        que invoca el bind_processor correcto (Vector._to_db) para convertir la
        lista de floats al formato de pgvector via protocolo binario de asyncpg.

        Esto reemplaza la versión anterior que construía el vector como string
        manual ("CAST(:query AS vector)") y sufría de:
          - 0 filas intermitentes por conflictos en el prepared-statement cache
            de asyncpg al reutilizar el statement con parámetros text muy largos.
          - N+1 queries (1 text query + 1 db.get() por fila resultado).

        Ahora se obtienen los objetos ORM directamente en una sola query.
        """
        cos_dist = FaceEncoding.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        stmt = (
            select(FaceEncoding, cos_dist)
            .order_by(cos_dist)
            .limit(int(top_k))
        )
        if distance_threshold is not None:
            stmt = stmt.where(cos_dist < float(distance_threshold))

        result = await self.db.execute(stmt)
        return [(enc, float(dist)) for enc, dist in result.all()]
