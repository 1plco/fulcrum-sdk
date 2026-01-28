"""Tests for DispatchClient."""

import os
from unittest.mock import patch

import httpx
import pytest
import respx
from pydantic import BaseModel

from fulcrum_sdk._internal.dispatch.client import DispatchClient, get_dispatch_client


class TestDispatchClientFromEnv:
    """Tests for DispatchClient.from_env()."""

    def test_from_env_with_all_vars(self):
        """Should create enabled client when all vars are set."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_MESSAGE_UUID": "msg-789",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is True

    def test_from_env_missing_url(self):
        """Should create disabled client when URL is missing."""
        env = {
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is False

    def test_from_env_missing_token(self):
        """Should create disabled client when token is missing."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is False

    def test_from_env_missing_ticket_uuid(self):
        """Should create disabled client when ticket_uuid is missing."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is False

    def test_from_env_with_optional_settings(self):
        """Should parse optional settings from env."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_DISPATCH_DEBUG": "1",
            "FULCRUM_DISPATCH_TIMEOUT_MS": "3000",
            "FULCRUM_DISPATCH_MAX_BYTES": "32768",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client._debug is True
            assert client._timeout_ms == 3000
            assert client._max_bytes == 32768

    def test_from_env_malformed_timeout_ms_raises(self):
        """Should raise ValueError when FULCRUM_DISPATCH_TIMEOUT_MS is not a valid integer."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_DISPATCH_TIMEOUT_MS": "not_a_number",
        }
        with patch.dict(os.environ, env, clear=True), pytest.raises(ValueError):
            DispatchClient.from_env()

    def test_from_env_malformed_max_bytes_raises(self):
        """Should raise ValueError when FULCRUM_DISPATCH_MAX_BYTES is not a valid integer."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_DISPATCH_MAX_BYTES": "invalid",
        }
        with patch.dict(os.environ, env, clear=True), pytest.raises(ValueError):
            DispatchClient.from_env()

    def test_from_env_prefers_run_token(self):
        """Should prefer FULCRUM_RUN_TOKEN over FULCRUM_DISPATCH_TOKEN."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_RUN_TOKEN": "preferred-token",
            "FULCRUM_DISPATCH_TOKEN": "deprecated-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is True
            assert client._dispatch_token == "preferred-token"

    def test_from_env_fallback_to_dispatch_token(self):
        """Should fallback to FULCRUM_DISPATCH_TOKEN when RUN_TOKEN is missing."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://localhost:3000/api/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "fallback-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = DispatchClient.from_env()
            assert client.enabled is True
            assert client._dispatch_token == "fallback-token"


class TestDispatchClientNoOp:
    """Tests for no-op client behavior."""

    def test_noop_dispatch_returns_false(self):
        """No-op client should return False for all dispatch calls."""
        client = DispatchClient()  # No config = no-op
        assert client.enabled is False
        assert client.dispatch("text", "Test") is False

    def test_noop_dispatch_text_returns_false(self):
        """No-op client should return False for dispatch_text."""
        client = DispatchClient()
        assert client.dispatch_text("Test") is False

    def test_noop_dispatch_json_returns_false(self):
        """No-op client should return False for dispatch_json."""
        client = DispatchClient()
        assert client.dispatch_json("Test", {"key": "value"}) is False

    def test_noop_dispatch_api_call_returns_false(self):
        """No-op client should return False for dispatch_api_call."""
        client = DispatchClient()
        assert client.dispatch_api_call("Test", "service", "op") is False

    def test_noop_dispatch_db_returns_false(self):
        """No-op client should return False for dispatch_db."""
        client = DispatchClient()
        assert client.dispatch_db("Test", "select", "users") is False


class TestDispatchClientSend:
    """Tests for DispatchClient sending behavior."""

    @respx.mock
    def test_dispatch_success(self):
        """Should return True on successful dispatch."""
        route = respx.post("http://test/dispatch").mock(
            return_value=httpx.Response(200, json={"uuid": "abc"})
        )

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch("text", "Test message")
        assert result is True
        assert route.called

    @respx.mock
    def test_dispatch_server_error(self):
        """Should return False on server error."""
        respx.post("http://test/dispatch").mock(return_value=httpx.Response(500))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch("text", "Test")
        assert result is False

    @respx.mock
    def test_dispatch_timeout(self):
        """Should return False on timeout."""
        respx.post("http://test/dispatch").mock(side_effect=httpx.TimeoutException("timeout"))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
            timeout_ms=100,
        )
        result = client.dispatch("text", "Test")
        assert result is False

    @respx.mock
    def test_dispatch_network_error(self):
        """Should return False on network error."""
        respx.post("http://test/dispatch").mock(
            side_effect=httpx.ConnectError("connection failed")
        )

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch("text", "Test")
        assert result is False

    @respx.mock
    def test_dispatch_sends_correct_payload(self):
        """Should send correctly structured payload."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket-123",
            run_uuid="run-456",
            message_uuid="msg-789",
        )
        client.dispatch("api_call", "Called API", {"service": "test"})

        request = route.calls.last.request
        body = request.content.decode()
        assert "ticket-123" in body
        assert "run-456" in body
        assert "msg-789" in body
        assert "api_call" in body
        assert "Called API" in body

    @respx.mock
    def test_dispatch_sends_auth_header(self):
        """Should send authorization header."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="secret-token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        client.dispatch("text", "Test")

        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer secret-token"

    @respx.mock
    def test_dispatch_redacts_payload(self):
        """Should redact sensitive keys in payload."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        client.dispatch("json", "Test", {"api_key": "secret123", "data": "visible"})

        request = route.calls.last.request
        body = request.content.decode()
        assert "secret123" not in body
        assert "[REDACTED]" in body
        assert "visible" in body

    @respx.mock
    def test_dispatch_truncates_long_summary(self):
        """Should truncate summary exceeding max length."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        long_summary = "x" * 600
        result = client.dispatch("text", long_summary)

        assert result is True
        request = route.calls.last.request
        body = request.content.decode()
        # Should be truncated to 512 chars with ...
        assert "..." in body


class TestConvenienceMethods:
    """Tests for convenience dispatch methods."""

    @respx.mock
    def test_dispatch_text(self):
        """Should dispatch text event."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch_text("Message sent", "Additional details")

        assert result is True
        body = route.calls.last.request.content.decode()
        assert '"kind":"text"' in body
        assert "Additional details" in body

    @respx.mock
    def test_dispatch_api_call(self):
        """Should dispatch API call event."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch_api_call(
            "Sent SMS",
            service="twilio",
            operation="send_sms",
            to="+1234567890",
        )

        assert result is True
        body = route.calls.last.request.content.decode()
        assert '"kind":"api_call"' in body
        assert "twilio" in body
        assert "send_sms" in body
        assert "+1234567890" in body

    @respx.mock
    def test_dispatch_db(self):
        """Should dispatch DB event."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch_db("Inserted users", "insert", "users", rows=5)

        assert result is True
        body = route.calls.last.request.content.decode()
        assert '"kind":"db"' in body
        assert '"table":"users"' in body
        assert '"count":5' in body

    @respx.mock
    def test_dispatch_model(self):
        """Should dispatch model event with data."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        class UserProfile(BaseModel):
            name: str
            email: str

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        model = UserProfile(name="Test", email="test@example.com")
        result = client.dispatch_model("Validated user", model, input_summary="Raw user data")

        assert result is True
        body = route.calls.last.request.content.decode()
        assert '"kind":"model"' in body
        assert "UserProfile" in body
        assert "Raw user data" in body
        # Verify data field contains serialized model values
        assert '"data":' in body
        assert '"name":"Test"' in body
        assert '"email":"test@example.com"' in body

    @respx.mock
    def test_dispatch_external_ref(self):
        """Should dispatch external ref event."""
        route = respx.post("http://test/dispatch").mock(return_value=httpx.Response(200))

        client = DispatchClient(
            dispatch_url="http://test/dispatch",
            dispatch_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.dispatch_external_ref(
            "Browser task started",
            provider="browser-use",
            ref_type="task",
            ref_id="task-123",
            url="http://example.com",
        )

        assert result is True
        body = route.calls.last.request.content.decode()
        assert '"kind":"external_ref"' in body
        assert "browser-use" in body
        assert "task-123" in body


class TestGetDispatchClient:
    """Tests for get_dispatch_client helper function."""

    def test_returns_client(self):
        """Should return a DispatchClient instance."""
        with patch.dict(os.environ, {}, clear=True):
            client = get_dispatch_client()
            assert isinstance(client, DispatchClient)

    def test_uses_from_env(self):
        """Should configure from environment."""
        env = {
            "FULCRUM_DISPATCH_URL": "http://test/dispatch",
            "FULCRUM_DISPATCH_TOKEN": "token",
            "FULCRUM_TICKET_UUID": "ticket",
            "FULCRUM_RUN_UUID": "run",
        }
        with patch.dict(os.environ, env, clear=True):
            client = get_dispatch_client()
            assert client.enabled is True
