"""Environment-backed application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables and an optional `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "tracelink"
    app_env: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://tracelink:tracelink@localhost:5432/tracelink"
    database_echo: bool = False

    @field_validator("database_url")
    @classmethod
    def validate_async_postgresql_url(cls, value: str) -> str:
        """Require SQLAlchemy's asyncpg PostgreSQL dialect."""
        if not value.startswith("postgresql+asyncpg://"):
            message = "DATABASE_URL must use the postgresql+asyncpg dialect"
            raise ValueError(message)
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
