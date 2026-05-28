from __future__ import annotations

"""
Application settings — loaded from environment variables via pydantic-settings.
All sensitive values must be provided via .env (never hardcoded).
"""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "RollCall API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str  # openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # ── Database ───────────────────────────────────────────────────────────────
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "rollcall"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Assembled async DSN (computed)
    DATABASE_URL: PostgresDsn | None = None

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if self.DATABASE_URL is None:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        return self

    # ── Face Recognition ───────────────────────────────────────────────────────
    # ArcFace ofrece mejor precision que VGG-Face en condiciones reales
    FACE_MODEL_NAME: str = "ArcFace"
    FACE_DETECTOR_BACKEND: str = "retinaface"
    # Umbral de distancia coseno para ArcFace. Recomendado DeepFace: 0.68.
    # 0.40 = muy estricto (rechaza matches validos por leve variacion de luz/angulo).
    # 0.55 = equilibrio: rechaza falsos positivos y acepta variaciones razonables.
    # 0.68 = permisivo (default de DeepFace).
    FACE_DISTANCE_THRESHOLD: float = 0.55
    FACE_ENFORCE_DETECTION: bool = True
    FACE_REGISTRATION_SAMPLES: int = 5

    # ── CORS ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Use as a FastAPI dependency: Depends(get_settings).
    """
    return Settings()
