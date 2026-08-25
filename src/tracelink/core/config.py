"""Environment-backed application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


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
        """Normalize standard provider URLs to SQLAlchemy's asyncpg dialect."""
        url = make_url(value)
        if url.drivername not in {"postgres", "postgresql", "postgresql+asyncpg"}:
            message = "DATABASE_URL must be a PostgreSQL URL"
            raise ValueError(message)

        query = dict(url.query)
        ssl_mode = query.pop("sslmode", None)
        query.pop("channel_binding", None)
        if ssl_mode is not None:
            query.setdefault("ssl", ssl_mode)

        return url.set(
            drivername="postgresql+asyncpg",
            query=query,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
