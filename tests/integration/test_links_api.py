"""HTTP integration tests for short-link workflows."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.db.models import Link

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


async def test_create_link(api_client: AsyncClient) -> None:
    response = await api_client.post(
        "/api/v1/links",
        json={
            "original_url": "https://example.com/articles/trace-link",
            "custom_slug": "portfolio",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "portfolio"
    assert body["original_url"] == "https://example.com/articles/trace-link"
    assert body["short_url"] == "http://testserver/portfolio"
    assert body["is_active"] is True


async def test_redirect_records_click_and_updates_stats(api_client: AsyncClient) -> None:
    create_response = await api_client.post(
        "/api/v1/links",
        json={"original_url": "https://example.com/destination", "custom_slug": "tracked"},
    )
    assert create_response.status_code == 201

    redirect_response = await api_client.get(
        "/tracked",
        headers={"referer": "https://referrer.example/", "user-agent": "tracelink-test"},
    )

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/destination"

    stats_response = await api_client.get("/api/v1/links/tracked/stats")
    assert stats_response.status_code == 200
    body = stats_response.json()
    assert body["slug"] == "tracked"
    assert body["total_clicks"] == 1
    assert body["first_clicked_at"] is not None
    assert body["last_clicked_at"] is not None
    assert len(body["clicks_by_day"]) == 1
    assert body["clicks_by_day"][0]["clicks"] == 1


async def test_duplicate_custom_slug_returns_conflict(api_client: AsyncClient) -> None:
    payload = {"original_url": "https://example.com", "custom_slug": "duplicate"}

    first_response = await api_client.post("/api/v1/links", json=payload)
    second_response = await api_client.post("/api/v1/links", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Slug 'duplicate' is unavailable"}


async def test_unknown_slug_returns_not_found(api_client: AsyncClient) -> None:
    response = await api_client.get("/missing-slug")

    assert response.status_code == 404
    assert response.json() == {"detail": "Link with slug 'missing-slug' was not found"}


async def test_expired_link_returns_gone(
    api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    expired_link = Link(
        short_code="expired",
        original_url="https://example.com/expired",
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    db_session.add(expired_link)
    await db_session.commit()

    response = await api_client.get("/expired")

    assert response.status_code == 410
    assert response.json() == {"detail": "Link with slug 'expired' is expired"}


async def test_stats_for_unknown_slug_returns_not_found(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/links/unknown/stats")

    assert response.status_code == 404
    assert response.json() == {"detail": "Link with slug 'unknown' was not found"}
