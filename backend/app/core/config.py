"""
Application Configuration and Settings Module.

Uses Pydantic v2 BaseSettings to load, validate, and type-cast environment variables.

Why this exists:
1. Prevents hardcoded credentials and configuration drift across environments (dev, test, prod).
2. Fails fast at startup if required configuration (database credentials, secrets) is invalid.
3. Automatically serializes/deserializes complex types such as CORS origin lists.
"""

from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    CloudForge application configuration settings.
    Automatically loaded from .env file or host environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # General Application & Environment
    PROJECT_NAME: str = "CloudForge API"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security & Tokens (Secret keys MUST be overridden in production via environment variables)
    SECRET_KEY: str = "supersecret_cloudforge_dev_jwt_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Database Configuration (PostgreSQL 16)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "cloudforge"
    POSTGRES_PASSWORD: str = "cloudforge_secret_pw"
    POSTGRES_DB: str = "cloudforge_db"

    # Asynchronous Database Connection URL for SQLAlchemy 2.0 + asyncpg
    DATABASE_URL: str = "postgresql+asyncpg://cloudforge:cloudforge_secret_pw@localhost:5433/cloudforge_db"

    # Database Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # CORS Allowed Origins (Supports list or comma-separated string)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Allows passing CORS origins as either a JSON array or a comma-separated string.
        Ensures trailing slashes are trimmed for strict origin matching.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).rstrip("/") for i in v]
        elif isinstance(v, str):
            import json
            return [str(i).rstrip("/") for i in json.loads(v)]
        raise ValueError("Invalid CORS origins")


settings = Settings()
