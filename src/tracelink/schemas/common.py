"""Shared API schemas."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error payload returned by the API."""

    detail: str
