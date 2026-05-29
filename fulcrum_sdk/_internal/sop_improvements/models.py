"""Pydantic models for semantic SOP improvements."""

from typing import Literal

from pydantic import BaseModel, Field

SopImprovementStatus = Literal[
    "open",
    "in_review",
    "drafted",
    "approved",
    "dismissed",
    "archived",
    "superseded",
]

TITLE_MAX_LENGTH = 256
DEDUPE_KEY_MAX_LENGTH = 256


class SopImprovement(BaseModel):
    """Semantic SOP improvement returned from the API."""

    uuid: str
    project_uuid: str
    sop_uuid: str | None = None
    source_ticket_uuid: str | None = None
    source_ticket_run_uuid: str | None = None
    source_guidance_request_uuid: str | None = None
    title: str
    description: str | None = None
    observed_gap: str | None = None
    suggested_change: str | None = None
    section_anchor: str | None = None
    severity: str = "normal"
    status: SopImprovementStatus = "open"
    dedupe_key: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class SopImprovementCreate(BaseModel):
    """Payload for creating a semantic SOP improvement."""

    title: str = Field(max_length=TITLE_MAX_LENGTH)
    description: str | None = None
    observed_gap: str | None = None
    suggested_change: str | None = None
    section_anchor: str | None = None
    severity: str = "normal"
    dedupe_key: str | None = Field(default=None, max_length=DEDUPE_KEY_MAX_LENGTH)
    source_guidance_request_uuid: str | None = None
