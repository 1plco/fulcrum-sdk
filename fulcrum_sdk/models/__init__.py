"""Shared public SDK models."""

from typing import Any

from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata returned by v1 list endpoints."""

    has_more: bool = Field(alias="hasMore")
    next_cursor: str | None = Field(default=None, alias="nextCursor")


JsonDict = dict[str, Any]

__all__ = ["JsonDict", "PaginationMeta"]
