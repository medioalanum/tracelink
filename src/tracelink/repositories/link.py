"""Persistence operations for shortened links."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.db.models import Link


class LinkRepository:
    """Read and write `Link` records using an async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_slug(self, slug: str) -> Link | None:
        """Return the link matching a slug, if one exists."""
        result = await self._session.execute(select(Link).where(Link.short_code == slug))
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        """Return whether a slug is already persisted."""
        result = await self._session.execute(select(Link.id).where(Link.short_code == slug))
        return result.scalar_one_or_none() is not None

    async def add(self, link: Link) -> Link:
        """Add and refresh a link without owning the transaction boundary."""
        self._session.add(link)
        await self._session.flush()
        await self._session.refresh(link)
        return link
