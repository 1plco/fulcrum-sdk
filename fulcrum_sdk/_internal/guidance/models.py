"""Pydantic models for Fulcrum guidance requests."""

from typing import Any

from pydantic import BaseModel, Field

CONTEXT_MAX_SIZE_BYTES = 64 * 1024
QUESTION_MAX_LENGTH = 4000
SOP_SECTION_MAX_LENGTH = 512


class GuidanceRequestResult(BaseModel):
    """Accepted guidance request returned by the Fulcrum API."""

    request_uuid: str
    status: str = "pending"
    guidance_request: dict[str, Any] | None = None


class GuidanceSeek(BaseModel):
    """Payload for asking the user for SOP guidance."""

    question: str = Field(min_length=1, max_length=QUESTION_MAX_LENGTH)
    severity: str = Field(default="severe", max_length=64)
    sop_section: str | None = Field(default=None, max_length=SOP_SECTION_MAX_LENGTH)
    context: dict[str, Any] | None = None
