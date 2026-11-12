"""
TRUSTLENS AI - Centralized Application Configuration
Manages environment variables, security secrets, database configuration, and limits.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    # Application Info
    APP_NAME: str = "TRUSTLENS AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", description="development | staging | production")
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Security & JWT
    SECRET_KEY: str = Field(
        default="trustlens-super-secret-jwt-key-2026-production-grade-encryption-change-me",
        description="JWT HMAC Secret Key",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ADMIN_DEFAULT_EMAIL: str = "admin@trustlens.ai"
    ADMIN_DEFAULT_PASSWORD: str = "Admin@TrustLens2026!"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,https://trustlens.vercel.app"

    @property
    def cors_origins(self) -> List[str]:
        return [orig.strip() for orig in self.ALLOWED_ORIGINS.split(",") if orig.strip()]

    # Database Settings (MongoDB Atlas)
    MONGODB_URI: str = Field(default="mongodb://localhost:27017", description="MongoDB Atlas Connection URI")
    MONGODB_DB_NAME: str = Field(default="trustlens_ai", description="Database Name")
    MONGODB_TIMEOUT_MS: int = 3000

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120
    AUTH_RATE_LIMIT_PER_MINUTE: int = 20

    # Uploads & File Size Limits
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/bmp"]

    # ML Runtime Configuration
    ML_ARTIFACTS_DIR: str = "ml/artifacts"
    ENABLE_CALIBRATED_SCORES: bool = True
    SIMILARITY_THRESHOLD_DEFAULT: float = 0.55

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = AppSettings()

