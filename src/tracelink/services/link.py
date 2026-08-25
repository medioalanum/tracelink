"""Business logic for creating shortened links."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.core.exceptions import SlugConflictError
from tracelink.db.models import Link
from tracelink.repositories.link import LinkRepository
from tracelink.schemas import LinkCreate
from tracelink.utils.short_code import generate_slug, is_reserved_slug

MAX_SLUG_GENERATION_ATTEMPTS = 10


class LinkService:
    """Allocate unique slugs and create links transactionally."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._links = LinkRepository(session)

    async def create(self, payload: LinkCreate) -> Link:
        """Create a link using a custom or generated collision-safe slug."""
        if payload.custom_slug is not None:
            return await self._create_with_slug(payload, payload.custom_slug, retry=False)

        for _ in range(MAX_SLUG_GENERATION_ATTEMPTS):
            slug = generate_slug()
            if await self._links.slug_exists(slug):
                continue
            try:
                return await self._create_with_slug(payload, slug, retry=True)
            except SlugConflictError:
                continue

        message = "Unable to allocate a unique slug"
        raise RuntimeError(message)

    async def _create_with_slug(
        self,
        payload: LinkCreate,
        slug: str,
        *,
        retry: bool,
    ) -> Link:
        if is_reserved_slug(slug) or await self._links.slug_exists(slug):
            raise SlugConflictError(slug)

        link = Link(
            short_code=slug,
            original_url=str(payload.original_url),
            expires_at=payload.expires_at,
        )
        try:
            await self._links.add(link)
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            if retry:
                raise SlugConflictError(slug) from error
            raise SlugConflictError(slug) from error
        return link
