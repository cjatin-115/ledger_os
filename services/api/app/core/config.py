from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "LedgerOS API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production", "testing", "test"] = "development"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/ledgeros"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    MFA_ENCRYPTION_KEY: str = "6pW5b9L0E5sXqJxV1R8w2eN7tY4uI3oP6aS9dF0gH2k="
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_ENABLED: bool = True
    STORAGE_BUCKET: str = "ledgeros-dev-bucket"
    STORAGE_BACKEND: str = "local"
    STORAGE_ENDPOINT_URL: str | None = None
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ACCESS_KEY_ID: str | None = None
    STORAGE_SECRET_ACCESS_KEY: str | None = None
    STORAGE_ROOT: str = "./storage"
    MAX_ATTACHMENT_SIZE_BYTES: int = 10 * 1024 * 1024
    GEMINI_API_KEY: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] | str = ["http://localhost:8081", "http://localhost:19006"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if v_str == "*" or v_str == '"*"' or v_str == "'*'":
                return ["*"]
            if v_str.startswith("[") and v_str.endswith("]"):
                import json

                try:
                    res = json.loads(v_str)
                    if isinstance(res, list):
                        return [str(x) for x in res]
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        if isinstance(v, list):
            return [str(x) for x in v]
        return ["*"]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
