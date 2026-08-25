"""Click analytics ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracelink.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from tracelink.db.models.link import Link


class ClickEvent(UUIDPrimaryKeyMixin, Base):
    """An immutable redirect event used as the analytics source of truth."""

    __tablename__ = "click_events"
    __table_args__ = (Index("ix_click_events_link_id_clicked_at", "link_id", "clicked_at"),)

    link_id: Mapped[UUID] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE"),
        nullable=False,
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    referrer: Mapped[str | None] = mapped_column(Text)
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_hash: Mapped[str | None] = mapped_column(String(64))

    link: Mapped[Link] = relationship(back_populates="click_events", lazy="raise")
