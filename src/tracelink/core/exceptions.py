"""Domain exceptions translated into API error responses."""


class LinkError(Exception):
    """Base class for link-domain failures."""


class LinkNotFoundError(LinkError):
    """Raised when a slug has no associated link."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Link with slug '{slug}' was not found")


class LinkUnavailableError(LinkError):
    """Raised when a link exists but can no longer redirect."""

    def __init__(self, slug: str, reason: str) -> None:
        super().__init__(f"Link with slug '{slug}' is {reason}")


class SlugConflictError(LinkError):
    """Raised when a requested slug cannot be allocated."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"Slug '{slug}' is unavailable")
