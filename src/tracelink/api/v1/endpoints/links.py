"""Link creation and analytics endpoints."""

from fastapi import APIRouter, Request, status

from tracelink.api.dependencies import AnalyticsServiceDependency, LinkServiceDependency
from tracelink.schemas import AnalyticsSummary, LinkCreate, LinkResponse

router = APIRouter(prefix="/links", tags=["links"])


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    request: Request,
    service: LinkServiceDependency,
) -> LinkResponse:
    """Create a new shortened link."""
    link = await service.create(payload)
    short_url = request.url_for("redirect_to_link", slug=link.short_code)
    return LinkResponse(
        id=link.id,
        slug=link.short_code,
        original_url=link.original_url,
        short_url=str(short_url),
        is_active=link.is_active,
        expires_at=link.expires_at,
        created_at=link.created_at,
    )


@router.get("/{slug}/stats", response_model=AnalyticsSummary)
async def get_link_stats(
    slug: str,
    service: AnalyticsServiceDependency,
) -> AnalyticsSummary:
    """Return aggregate click metrics for a slug."""
    return await service.get_summary(slug)
