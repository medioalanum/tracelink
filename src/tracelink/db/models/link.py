"""Short-link ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracelink.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from tracelink.db.models.click_event import ClickEvent


class Link(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A shortened destination URL and its lifecycle state."""

    __tablename__ = "links"

    short_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
    )
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    click_events: Mapped[list[ClickEvent]] = relationship(
        back_populates="link",
        cascade="all, delete-orphan",
        lazy="raise",
        passive_deletes=True,
    )
