"""Business logic for resolving links and recording redirects."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.core.exceptions import LinkNotFoundError, LinkUnavailableError
from tracelink.db.models import Link
from tracelink.repositories.click_event import ClickEventRepository
from tracelink.repositories.link import LinkRepository


class RedirectService:
    """Validate a redirect target and record its click event."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._links = LinkRepository(session)
        self._clicks = ClickEventRepository(session)

    async def resolve_and_record(
        self,
        slug: str,
        *,
        referrer: str | None,
        user_agent: str | None,
    ) -> Link:
        """Resolve an active link and persist its analytics event asynchronously."""
        link = await self._links.get_by_slug(slug)
        if link is None:
            raise LinkNotFoundError(slug)
        if not link.is_active:
            raise LinkUnavailableError(slug, "inactive")
        if link.expires_at is not None and link.expires_at <= datetime.now(UTC):
            raise LinkUnavailableError(slug, "expired")

        await self._clicks.add(
            link_id=link.id,
            referrer=referrer,
            user_agent=user_agent,
        )
        await self._session.commit()
        return link
