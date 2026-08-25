"""Collision-resistant short-code generation."""

import secrets
import string

DEFAULT_SLUG_LENGTH = 8
SLUG_ALPHABET = string.ascii_letters + string.digits + "-_"
RESERVED_SLUGS = frozenset(
    {
        "api",
        "docs",
        "health",
        "openapi.json",
        "ready",
        "redoc",
    }
)


def generate_slug(length: int = DEFAULT_SLUG_LENGTH) -> str:
    """Return a cryptographically secure, URL-safe random slug."""
    if length < 1:
        message = "slug length must be positive"
        raise ValueError(message)
    return "".join(secrets.choice(SLUG_ALPHABET) for _ in range(length))


def is_reserved_slug(slug: str) -> bool:
    """Return whether a slug conflicts with an application route."""
    return slug.casefold() in RESERVED_SLUGS
