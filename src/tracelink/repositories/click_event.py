"""Persistence and aggregation operations for click events."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.db.models import ClickEvent


@dataclass(frozen=True, slots=True)
class DailyClickMetric:
    """Click count for a single UTC day."""

    date: date
    clicks: int


@dataclass(frozen=True, slots=True)
class ClickMetrics:
    """Aggregate click metrics returned by the repository."""

    total_clicks: int
    first_clicked_at: datetime | None
    last_clicked_at: datetime | None
    clicks_by_day: list[DailyClickMetric]


class ClickEventRepository:
    """Write click events and compute aggregate metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        link_id: UUID,
        referrer: str | None,
        user_agent: str | None,
    ) -> ClickEvent:
        """Persist one redirect event without storing a raw IP address."""
        event = ClickEvent(
            link_id=link_id,
            referrer=referrer,
            user_agent=user_agent,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def summarize(self, link_id: UUID) -> ClickMetrics:
        """Return total, boundary timestamps, and UTC daily counts for a link."""
        summary_result = await self._session.execute(
            select(
                func.count(ClickEvent.id),
                func.min(ClickEvent.clicked_at),
                func.max(ClickEvent.clicked_at),
            ).where(ClickEvent.link_id == link_id)
        )
        total_clicks, first_clicked_at, last_clicked_at = summary_result.one()

        day_expression = cast(ClickEvent.clicked_at, Date)
        daily_result = await self._session.execute(
            select(day_expression, func.count(ClickEvent.id))
            .where(ClickEvent.link_id == link_id)
            .group_by(day_expression)
            .order_by(day_expression)
        )
        clicks_by_day = [
            DailyClickMetric(date=row_date, clicks=row_count)
            for row_date, row_count in daily_result.all()
        ]

        return ClickMetrics(
            total_clicks=total_clicks,
            first_clicked_at=first_clicked_at,
            last_clicked_at=last_clicked_at,
            clicks_by_day=clicks_by_day,
        )
