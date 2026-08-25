"""Request and response schemas for shortened links."""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import AnyHttpUrl, AwareDatetime, BaseModel, Field, field_validator


class LinkCreate(BaseModel):
    """Payload accepted when creating a short link."""

    original_url: AnyHttpUrl
    custom_slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    expires_at: AwareDatetime | None = None

    @field_validator("expires_at")
    @classmethod
    def validate_future_expiration(cls, value: AwareDatetime | None) -> AwareDatetime | None:
        """Reject links that are already expired at creation time."""
        if value is not None and value <= datetime.now(UTC):
            message = "expires_at must be in the future"
            raise ValueError(message)
        return value


class LinkResponse(BaseModel):
    """Public representation of a shortened link."""

    id: UUID
    slug: str
    original_url: AnyHttpUrl
    short_url: AnyHttpUrl
    is_active: bool
    expires_at: AwareDatetime | None
    created_at: AwareDatetime
