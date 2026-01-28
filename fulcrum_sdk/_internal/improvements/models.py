"""Pydantic models for Fulcrum improvements entries.

These models define the structure for improvements data.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

# =============================================================================
# Constants
# =============================================================================

PAYLOAD_MAX_SIZE_BYTES = 64 * 1024  # 64KB
SCHEMA_VERSION = 1

# Valid improvement statuses
ImprovementStatus = Literal["open", "in_progress", "resolved", "dismissed"]

# =============================================================================
# Response Models
# =============================================================================


class Improvement(BaseModel):
    """Improvement record returned from the API.

    Represents an improvement suggestion or issue identified during execution.
    """

    uuid: str
    project_uuid: str
    ticket_uuid: str | None = None
    run_uuid: str | None = None
    title: str
    description: str | None = None
    status: ImprovementStatus = "open"
    dedupe_key: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# =============================================================================
# Request Models
# =============================================================================


class ImprovementCreate(BaseModel):
    """Payload for creating a new improvement.

    Required fields:
        title: Brief title for the improvement (max 256 chars)

    Optional fields:
        description: Detailed description of the improvement
        dedupe_key: Key for deduplication (prevents duplicates)
        status: Initial status (default: 'open')
    """

    title: str = Field(max_length=256)
    description: str | None = None
    dedupe_key: str | None = Field(default=None, max_length=256)
    status: ImprovementStatus = "open"


class ImprovementUpdate(BaseModel):
    """Payload for updating an existing improvement.

    All fields are optional - only provided fields are updated.
    """

    title: str | None = Field(default=None, max_length=256)
    description: str | None = None
    status: ImprovementStatus | None = None


# =============================================================================
# Event Models
# =============================================================================


class ImprovementEvent(BaseModel):
    """Event emission payload for improvement actions.

    Used to record actions taken on improvements.
    """

    improvement_uuid: str
    action: str = Field(max_length=64)
    payload: dict[str, Any] | None = None

    model_config = {"extra": "allow"}
