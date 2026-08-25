"""FastAPI application factory and entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from tracelink.api.v1.endpoints.health import router as health_router
from tracelink.api.v1.endpoints.redirects import router as redirects_router
from tracelink.api.v1.router import router as api_v1_router
from tracelink.api.web import router as web_router
from tracelink.core.config import get_settings
from tracelink.core.exceptions import (
    LinkNotFoundError,
    LinkUnavailableError,
    SlugConflictError,
)
from tracelink.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Dispose of database resources when the application stops."""
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    @application.exception_handler(LinkNotFoundError)
    async def handle_link_not_found(
        _: Request,
        error: LinkNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )

    @application.exception_handler(LinkUnavailableError)
    async def handle_link_unavailable(
        _: Request,
        error: LinkUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content={"detail": str(error)},
        )

    @application.exception_handler(SlugConflictError)
    async def handle_slug_conflict(
        _: Request,
        error: SlugConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )

    application.include_router(health_router)
    application.include_router(api_v1_router, prefix="/api/v1")
    application.include_router(web_router)
    application.include_router(redirects_router)
    return application


app = create_app()
