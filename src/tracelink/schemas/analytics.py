"""Response schemas for link analytics."""

from datetime import date

from pydantic import AwareDatetime, BaseModel, Field


class DailyClickCount(BaseModel):
    """Number of clicks recorded on one UTC calendar day."""

    date: date
    clicks: int = Field(ge=0)


class AnalyticsSummary(BaseModel):
    """Aggregate click metrics for a short link."""

    slug: str
    total_clicks: int = Field(ge=0)
    first_clicked_at: AwareDatetime | None
    last_clicked_at: AwareDatetime | None
    clicks_by_day: list[DailyClickCount]
