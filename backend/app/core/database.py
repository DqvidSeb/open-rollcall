"""
Async SQLAlchemy engine + session factory.

All DB access uses async sessions. Never import `engine` directly in
business logic — always go through `get_db` or `AsyncSessionLocal`.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# NullPool is used in tests to avoid connection issues with pytest-asyncio.
# In production the default AsyncAdaptedQueuePool is used.
_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "pool_size": settings.DATABASE_POOL_SIZE,
    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
    "pool_pre_ping": True,  # discard stale connections
}

engine = create_async_engine(str(settings.DATABASE_URL), **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a transactional async DB session.
    Automatically rolls back on exception and closes the session.

    Usage:
        async def route(db: AsyncSession = Depends(get_db)): ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
