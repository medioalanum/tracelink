"""Tests for the browser interface."""

import pytest
from httpx import ASGITransport, AsyncClient

from tracelink.main import app


@pytest.mark.asyncio
async def test_home_page_serves_shortener_interface() -> None:
    """The root route renders the URL shortener interface."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "TraceLink" in response.text
    assert 'id="create-form"' in response.text
    assert 'fetch("/api/v1/links"' in response.text


@pytest.mark.asyncio
async def test_favicon_does_not_resolve_a_short_link() -> None:
    """Browser favicon requests are handled without database access."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/favicon.ico")

    assert response.status_code == 204
