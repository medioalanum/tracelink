"""Version 1 API router."""

from fastapi import APIRouter

from tracelink.api.v1.endpoints.links import router as links_router

router = APIRouter()
router.include_router(links_router)
