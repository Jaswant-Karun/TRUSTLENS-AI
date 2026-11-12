"""
TRUSTLENS AI - Application Configuration
Centralized configuration management using Pydantic Settings.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Metadata
    APP_NAME: str = "TRUSTLENS AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Security & CORS
    SECRET_KEY: str = "trustlens-dev-secret-key-change-in-production-123456789"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,https://trustlens.vercel.app"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Database Settings (MongoDB Atlas)
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "trustlens_ai"
    MONGODB_TIMEOUT_MS: int = 3000

    # ML Runtime Configuration
    ML_ARTIFACTS_DIR: str = "ml/artifacts"
    ML_CPU_THREADS: int = 8
    ENABLE_CALIBRATED_SCORES: bool = True

    # n8n Automation
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/threat-alert"
    N8N_API_KEY: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

