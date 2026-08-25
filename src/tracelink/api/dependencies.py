"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracelink.db.session import get_db_session
from tracelink.services.analytics import AnalyticsService
from tracelink.services.link import LinkService
from tracelink.services.redirect import RedirectService

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_link_service(session: DatabaseSession) -> LinkService:
    """Build a link service for the current request session."""
    return LinkService(session)


def get_redirect_service(session: DatabaseSession) -> RedirectService:
    """Build a redirect service for the current request session."""
    return RedirectService(session)


def get_analytics_service(session: DatabaseSession) -> AnalyticsService:
    """Build an analytics service for the current request session."""
    return AnalyticsService(session)


LinkServiceDependency = Annotated[LinkService, Depends(get_link_service)]
RedirectServiceDependency = Annotated[RedirectService, Depends(get_redirect_service)]
AnalyticsServiceDependency = Annotated[AnalyticsService, Depends(get_analytics_service)]
