"""Tests for environment-backed application settings."""

import pytest
from pydantic import ValidationError

from tracelink.core.config import Settings


def test_settings_accept_async_postgresql_url() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://user:password@localhost:5432/test_db",
    )

    assert settings.app_name == "tracelink"
    assert settings.database_url.startswith("postgresql+asyncpg://")


def test_settings_reject_non_async_database_url() -> None:
    with pytest.raises(ValidationError, match="postgresql\\+asyncpg"):
        Settings(_env_file=None, database_url="postgresql://localhost/test_db")
