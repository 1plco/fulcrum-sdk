"""Pydantic models for Fulcrum dispatch entries.

These models match the TypeScript contract in webapp/types/dispatch.ts.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# Constants
# =============================================================================

SUMMARY_MAX_LENGTH = 512
PAYLOAD_MAX_SIZE_BYTES = 64 * 1024  # 64KB
PAYLOAD_MAX_DEPTH = 3
KIND_MAX_LENGTH = 64
SOURCE_MAX_LENGTH = 32
SCHEMA_VERSION = 1

# =============================================================================
# Base Dispatch Entry
# =============================================================================


class DispatchEntry(BaseModel):
    """Base dispatch entry sent to the API.

    Required fields:
        ticket_uuid: UUID of the ticket this dispatch belongs to
        run_uuid: UUID of the run (execution instance)
        kind: Classification of the dispatch (e.g., 'text', 'api_call', 'db')
        summary: Human-readable summary, <= 512 chars, single line, present tense

    Optional fields:
        message_uuid: Reference to a ticket message
        payload: Additional structured data, JSON object, <= 64KB
        source: Origin of the dispatch (default: "sdk")
        schema_version: Schema version for forward compatibility (default: 1)
        client_ts: Client timestamp for debugging (ISO string)
    """

    ticket_uuid: str
    run_uuid: str
    kind: str = Field(max_length=KIND_MAX_LENGTH)
    summary: str = Field(max_length=SUMMARY_MAX_LENGTH)

    message_uuid: str | None = None
    payload: dict[str, Any] | None = None
    source: str = Field(default="sdk", max_length=SOURCE_MAX_LENGTH)
    schema_version: int = SCHEMA_VERSION
    client_ts: str | None = None

    @field_validator("summary")
    @classmethod
    def summary_single_line(cls, v: str) -> str:
        if "\n" in v:
            raise ValueError("summary must be a single line (no newlines)")
        return v

    @field_validator("kind")
    @classmethod
    def kind_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("kind must not be empty")
        return v


# =============================================================================
# Kind-Specific Payload Models
# =============================================================================


class TextPayload(BaseModel):
    """Payload structure for text kind.

    Use for general text milestones (payload is optional).
    """

    text: str | None = None

    model_config = {"extra": "allow"}


class JsonPayload(BaseModel):
    """Payload structure for json kind.

    Use for JSON parsing/extraction operations.
    """

    fields_extracted: list[str] | None = None
    confidence: float | None = None

    model_config = {"extra": "allow"}


class ApiCallPayload(BaseModel):
    """Payload structure for api_call kind.

    Use when the primary user-relevant event is the action taken.
    """

    service: str
    operation: str

    model_config = {"extra": "allow"}


class ExternalRefPayload(BaseModel):
    """Payload structure for external_ref kind.

    Use when the primary value is a pointer to something external.
    """

    provider: str
    ref_type: str
    ref_id: str
    url: str | None = None

    model_config = {"extra": "allow"}


class DbPayload(BaseModel):
    """Payload structure for db kind.

    Use for database operations (include counts, not raw rows).
    """

    table: str
    operation: str  # 'insert', 'update', 'delete', 'select'
    count: int | None = None
    query: str | None = None

    model_config = {"extra": "allow"}


class ModelPayload(BaseModel):
    """Payload structure for model kind.

    Use to display Pydantic model data as intermediate steps.
    """

    model_name: str
    data: dict[str, Any] | None = None
    input_summary: str | None = None
    output_summary: str | None = None

    model_config = {"extra": "allow"}
