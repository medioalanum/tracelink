"""Tests for the initial SQLAlchemy model metadata."""

from tracelink.db.base import Base
from tracelink.db.models import ClickEvent, Link


def test_model_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {"click_events", "links"}


def test_short_code_is_unique() -> None:
    short_code = Link.__table__.c.short_code

    assert short_code.unique is True


def test_click_event_foreign_key_cascades_on_delete() -> None:
    foreign_key = next(iter(ClickEvent.__table__.c.link_id.foreign_keys))

    assert foreign_key.target_fullname == "links.id"
    assert foreign_key.ondelete == "CASCADE"
