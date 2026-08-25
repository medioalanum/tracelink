"""Health endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Report that the application process is serving requests."""
    return {"status": "ok"}
