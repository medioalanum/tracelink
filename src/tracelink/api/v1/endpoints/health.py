"""Health and database readiness endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from tracelink.api.dependencies import DatabaseSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Report that the application process is serving requests."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(session: DatabaseSession) -> dict[str, str]:
    """Report whether the application can query its configured database."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from error
    return {"status": "ready"}
