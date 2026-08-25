"""Shared pytest fixtures for PostgreSQL integration tests."""

from collections.abc import AsyncIterator, Iterator
from shutil import which

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from tracelink.db.base import Base
from tracelink.db.models import ClickEvent, Link

POSTGRES_IMAGE = "postgres:17-alpine"
DATABASE_TABLES = (ClickEvent.__tablename__, Link.__tablename__)


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Start an isolated PostgreSQL container and return an async connection URL."""
    if which("docker") is None:
        pytest.skip("Docker is required for PostgreSQL integration tests")

    with PostgresContainer(POSTGRES_IMAGE) as postgres:
        sync_url = make_url(postgres.get_connection_url())
        async_url = sync_url.set(drivername="postgresql+asyncpg")
        yield async_url.render_as_string(hide_password=False)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    """Create the test schema once and dispose of it after the test session."""
    engine = create_async_engine(postgres_url, pool_pre_ping=True)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield an isolated session and clear persisted rows after each test."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()

    table_names = ", ".join(DATABASE_TABLES)
    async with test_engine.begin() as connection:
        await connection.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture(loop_scope="session")
async def api_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Return an HTTP client whose application uses the isolated test session."""
    from tracelink.db.session import get_db_session
    from tracelink.main import create_app

    application = create_app()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    application.dependency_overrides[get_db_session] = override_db_session
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        yield client

    application.dependency_overrides.clear()
