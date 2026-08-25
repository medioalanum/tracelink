"""Short-link redirect endpoints."""

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from tracelink.api.dependencies import RedirectServiceDependency

router = APIRouter(tags=["redirects"])


@router.get("/{slug}", name="redirect_to_link", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_link(
    slug: str,
    request: Request,
    service: RedirectServiceDependency,
) -> RedirectResponse:
    """Redirect to the destination URL and asynchronously record one click."""
    link = await service.resolve_and_record(
        slug,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse(url=link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
