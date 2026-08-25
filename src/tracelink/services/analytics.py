"""Business logic for retrieving link analytics."""

from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.core.exceptions import LinkNotFoundError
from tracelink.repositories.click_event import ClickEventRepository
from tracelink.repositories.link import LinkRepository
from tracelink.schemas import AnalyticsSummary, DailyClickCount


class AnalyticsService:
    """Retrieve aggregate click metrics for a slug."""

    def __init__(self, session: AsyncSession) -> None:
        self._links = LinkRepository(session)
        self._clicks = ClickEventRepository(session)

    async def get_summary(self, slug: str) -> AnalyticsSummary:
        """Return analytics for a link, including links that are no longer active."""
        link = await self._links.get_by_slug(slug)
        if link is None:
            raise LinkNotFoundError(slug)

        metrics = await self._clicks.summarize(link.id)
        return AnalyticsSummary(
            slug=slug,
            total_clicks=metrics.total_clicks,
            first_clicked_at=metrics.first_clicked_at,
            last_clicked_at=metrics.last_clicked_at,
            clicks_by_day=[
                DailyClickCount(date=item.date, clicks=item.clicks)
                for item in metrics.clicks_by_day
            ],
        )
