"""SQLAlchemy ORM models."""

from tracelink.db.models.click_event import ClickEvent
from tracelink.db.models.link import Link

__all__ = ["ClickEvent", "Link"]
