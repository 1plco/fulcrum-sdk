"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from fulcrum_sdk._internal.dispatch.models import (
    KIND_MAX_LENGTH,
    SUMMARY_MAX_LENGTH,
    ApiCallPayload,
    DbPayload,
    DispatchEntry,
    ExternalRefPayload,
    JsonPayload,
    ModelPayload,
    TextPayload,
)


class TestDispatchEntry:
    """Tests for DispatchEntry model."""

    def test_valid_entry(self):
        """Should create a valid dispatch entry."""
        entry = DispatchEntry(
            ticket_uuid="ticket-123",
            run_uuid="run-456",
            kind="text",
            summary="Test message",
        )
        assert entry.ticket_uuid == "ticket-123"
        assert entry.run_uuid == "run-456"
        assert entry.kind == "text"
        assert entry.summary == "Test message"
        assert entry.source == "sdk"
        assert entry.schema_version == 1

    def test_entry_with_all_fields(self):
        """Should create an entry with all optional fields."""
        entry = DispatchEntry(
            ticket_uuid="ticket-123",
            run_uuid="run-456",
            kind="api_call",
            summary="Called external API",
            message_uuid="msg-789",
            payload={"service": "test"},
            source="custom",
            schema_version=2,
            client_ts="2024-01-01T00:00:00Z",
        )
        assert entry.message_uuid == "msg-789"
        assert entry.payload == {"service": "test"}
        assert entry.source == "custom"
        assert entry.schema_version == 2
        assert entry.client_ts == "2024-01-01T00:00:00Z"

    def test_summary_max_length(self):
        """Should reject summary exceeding max length."""
        long_summary = "x" * (SUMMARY_MAX_LENGTH + 1)
        with pytest.raises(ValidationError) as exc_info:
            DispatchEntry(
                ticket_uuid="ticket-123",
                run_uuid="run-456",
                kind="text",
                summary=long_summary,
            )
        assert "summary" in str(exc_info.value)

    def test_summary_no_newlines(self):
        """Should reject summary with newlines."""
        with pytest.raises(ValidationError) as exc_info:
            DispatchEntry(
                ticket_uuid="ticket-123",
                run_uuid="run-456",
                kind="text",
                summary="Line 1\nLine 2",
            )
        assert "single line" in str(exc_info.value)

    def test_kind_max_length(self):
        """Should reject kind exceeding max length."""
        long_kind = "x" * (KIND_MAX_LENGTH + 1)
        with pytest.raises(ValidationError) as exc_info:
            DispatchEntry(
                ticket_uuid="ticket-123",
                run_uuid="run-456",
                kind=long_kind,
                summary="Test",
            )
        assert "kind" in str(exc_info.value)

    def test_kind_not_empty(self):
        """Should reject empty kind."""
        with pytest.raises(ValidationError) as exc_info:
            DispatchEntry(
                ticket_uuid="ticket-123",
                run_uuid="run-456",
                kind="",
                summary="Test",
            )
        assert "kind" in str(exc_info.value)

    def test_model_dump_excludes_none(self):
        """Should exclude None values when dumping."""
        entry = DispatchEntry(
            ticket_uuid="ticket-123",
            run_uuid="run-456",
            kind="text",
            summary="Test",
        )
        data = entry.model_dump(exclude_none=True)
        assert "message_uuid" not in data
        assert "payload" not in data
        assert "client_ts" not in data


class TestTextPayload:
    """Tests for TextPayload model."""

    def test_empty_payload(self):
        """Should allow empty payload."""
        payload = TextPayload()
        assert payload.text is None

    def test_with_text(self):
        """Should store text field."""
        payload = TextPayload(text="Some text content")
        assert payload.text == "Some text content"

    def test_extra_fields_allowed(self):
        """Should allow extra fields."""
        payload = TextPayload.model_validate({"text": "Content", "custom_field": "value"})
        assert payload.text == "Content"
        assert payload.model_dump()["custom_field"] == "value"


class TestJsonPayload:
    """Tests for JsonPayload model."""

    def test_basic_payload(self):
        """Should create basic JSON payload."""
        payload = JsonPayload(fields_extracted=["name", "email"])
        assert payload.fields_extracted == ["name", "email"]

    def test_with_confidence(self):
        """Should store confidence score."""
        payload = JsonPayload(confidence=0.95)
        assert payload.confidence == 0.95


class TestApiCallPayload:
    """Tests for ApiCallPayload model."""

    def test_required_fields(self):
        """Should require service and operation."""
        payload = ApiCallPayload(service="stripe", operation="create_charge")
        assert payload.service == "stripe"
        assert payload.operation == "create_charge"

    def test_extra_details(self):
        """Should allow extra operation details."""
        payload = ApiCallPayload.model_validate({
            "service": "twilio",
            "operation": "send_sms",
            "to": "+1234567890",
            "status": "sent",
        })
        data = payload.model_dump()
        assert data["to"] == "+1234567890"
        assert data["status"] == "sent"


class TestExternalRefPayload:
    """Tests for ExternalRefPayload model."""

    def test_required_fields(self):
        """Should require provider, ref_type, and ref_id."""
        payload = ExternalRefPayload(
            provider="browser-use",
            ref_type="task",
            ref_id="task-123",
        )
        assert payload.provider == "browser-use"
        assert payload.ref_type == "task"
        assert payload.ref_id == "task-123"
        assert payload.url is None

    def test_with_url(self):
        """Should store optional URL."""
        payload = ExternalRefPayload(
            provider="docs",
            ref_type="document",
            ref_id="doc-456",
            url="https://example.com/doc",
        )
        assert payload.url == "https://example.com/doc"


class TestDbPayload:
    """Tests for DbPayload model."""

    def test_basic_query(self):
        """Should create basic DB payload."""
        payload = DbPayload(table="users", operation="select")
        assert payload.table == "users"
        assert payload.operation == "select"
        assert payload.count is None

    def test_with_count(self):
        """Should store row count."""
        payload = DbPayload(table="orders", operation="insert", count=5)
        assert payload.count == 5

    def test_with_query(self):
        """Should store query string."""
        payload = DbPayload(
            table="products",
            operation="select",
            query="SELECT * FROM products WHERE active = true",
        )
        assert payload.query is not None
        assert "SELECT" in payload.query


class TestModelPayload:
    """Tests for ModelPayload model."""

    def test_basic_model(self):
        """Should create basic model payload."""
        payload = ModelPayload(model_name="UserProfile")
        assert payload.model_name == "UserProfile"
        assert payload.input_summary is None
        assert payload.output_summary is None

    def test_with_summaries(self):
        """Should store input/output summaries."""
        payload = ModelPayload(
            model_name="Order",
            input_summary="Raw order data",
            output_summary="Validated order object",
        )
        assert payload.input_summary == "Raw order data"
        assert payload.output_summary == "Validated order object"
