"""
Punto de entrada de la aplicación FastAPI.

Registra middlewares, routers, handlers de errores y eventos de lifespan.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────

async def _warmup_deepface() -> None:
    """
    Pre-carga el modelo ArcFace de DeepFace durante el startup del servidor.

    Sin esto, el primer request de reconocimiento incurre en ~20 segundos de
    latencia mientras TensorFlow inicializa los pesos del modelo. Con este
    warm-up el modelo queda listo antes de que llegue cualquier request.

    Se ejecuta en un thread para no bloquear el event loop de asyncio.
    """
    import os
    os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
    try:
        from deepface import DeepFace  # noqa: PLC0415
        logger.info("⏳ Pre-cargando modelo DeepFace '%s'...", settings.FACE_MODEL_NAME)
        await asyncio.to_thread(DeepFace.build_model, settings.FACE_MODEL_NAME)
        logger.info("✅ Modelo DeepFace '%s' listo", settings.FACE_MODEL_NAME)
    except Exception as exc:
        # No-fatal: si falla el warm-up el servidor igual arranca;
        # el primer request tendrá latencia alta pero no fallará.
        logger.warning("⚠️  DeepFace warm-up no disponible (no-fatal): %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 RollCall API starting — environment: %s", settings.ENVIRONMENT)
    await _warmup_deepface()
    yield
    logger.info("🛑 RollCall API shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"], include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": settings.APP_VERSION})
