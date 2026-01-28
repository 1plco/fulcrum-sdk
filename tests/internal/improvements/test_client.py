"""Tests for ImprovementsClient."""

import os
from unittest.mock import patch

import httpx
import pytest
import respx

from fulcrum_sdk._internal.improvements.client import (
    ImprovementsClient,
    get_improvements_client,
)


class TestImprovementsClientFromEnv:
    """Tests for ImprovementsClient.from_env()."""

    def test_from_env_with_all_vars(self):
        """Should create enabled client when all vars are set."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_PROJECT_UUID": "project-123",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is True

    def test_from_env_missing_url(self):
        """Should create disabled client when URL is missing."""
        env = {
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is False

    def test_from_env_missing_token(self):
        """Should create disabled client when token is missing."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is False

    def test_from_env_missing_run_uuid(self):
        """Should create disabled client when run_uuid is missing."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_RUN_TOKEN": "test-token",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is False

    def test_from_env_prefers_run_token(self):
        """Should prefer FULCRUM_RUN_TOKEN over FULCRUM_DISPATCH_TOKEN."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_RUN_TOKEN": "preferred-token",
            "FULCRUM_DISPATCH_TOKEN": "deprecated-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is True
            assert client._run_token == "preferred-token"

    def test_from_env_fallback_to_dispatch_token(self):
        """Should fallback to FULCRUM_DISPATCH_TOKEN when RUN_TOKEN is missing."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_DISPATCH_TOKEN": "fallback-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client.enabled is True
            assert client._run_token == "fallback-token"

    def test_from_env_with_optional_settings(self):
        """Should parse optional settings from env."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://localhost:3000/api/improvements",
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_IMPROVEMENTS_DEBUG": "1",
            "FULCRUM_IMPROVEMENTS_TIMEOUT_MS": "3000",
            "FULCRUM_IMPROVEMENTS_MAX_BYTES": "32768",
        }
        with patch.dict(os.environ, env, clear=True):
            client = ImprovementsClient.from_env()
            assert client._debug is True
            assert client._timeout_ms == 3000
            assert client._max_bytes == 32768


class TestImprovementsClientNoOp:
    """Tests for no-op client behavior."""

    def test_noop_list_returns_empty_list(self):
        """No-op client should return empty list for list_improvements."""
        client = ImprovementsClient()  # No config = no-op
        assert client.enabled is False
        assert client.list_improvements() == []

    def test_noop_create_returns_false(self):
        """No-op client should return False for create_improvement."""
        client = ImprovementsClient()
        assert client.create_improvement("Test") is False

    def test_noop_update_returns_false(self):
        """No-op client should return False for update_improvement."""
        client = ImprovementsClient()
        assert client.update_improvement("uuid", title="New") is False

    def test_noop_delete_returns_false(self):
        """No-op client should return False for delete_improvement."""
        client = ImprovementsClient()
        assert client.delete_improvement("uuid") is False

    def test_noop_emit_event_returns_false(self):
        """No-op client should return False for emit_improvement_event."""
        client = ImprovementsClient()
        assert client.emit_improvement_event("uuid", "action") is False


class TestImprovementsClientOperations:
    """Tests for ImprovementsClient CRUD operations."""

    @respx.mock
    def test_list_improvements_success(self):
        """Should return list of improvements on success."""
        route = respx.get("http://test/improvements").mock(
            return_value=httpx.Response(
                200,
                json={
                    "improvements": [
                        {
                            "uuid": "imp-1",
                            "project_uuid": "proj-1",
                            "title": "Test Improvement",
                            "status": "open",
                        }
                    ]
                },
            )
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.list_improvements()

        assert len(result) == 1
        assert result[0].uuid == "imp-1"
        assert result[0].title == "Test Improvement"
        assert route.called

    @respx.mock
    def test_list_improvements_server_error(self):
        """Should return empty list on server error."""
        respx.get("http://test/improvements").mock(return_value=httpx.Response(500))

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.list_improvements()
        assert result == []

    @respx.mock
    def test_create_improvement_success(self):
        """Should return True on successful create."""
        route = respx.post("http://test/improvements").mock(
            return_value=httpx.Response(201, json={"uuid": "new-uuid"})
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
            project_uuid="project",
            ticket_uuid="ticket",
        )
        result = client.create_improvement(
            title="New Improvement",
            description="A description",
            dedupe_key="key-123",
        )

        assert result is True
        assert route.called

        # Verify request body
        request = route.calls.last.request
        body = request.content.decode()
        assert "New Improvement" in body
        assert "run" in body
        assert "project" in body

    @respx.mock
    def test_create_improvement_server_error(self):
        """Should return False on server error."""
        respx.post("http://test/improvements").mock(return_value=httpx.Response(500))

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.create_improvement(title="Test")
        assert result is False

    @respx.mock
    def test_update_improvement_success(self):
        """Should return True on successful update."""
        route = respx.patch("http://test/improvements/uuid-123").mock(
            return_value=httpx.Response(200, json={"uuid": "uuid-123"})
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.update_improvement("uuid-123", title="Updated", status="resolved")

        assert result is True
        assert route.called

    @respx.mock
    def test_update_improvement_no_valid_fields(self):
        """Should return False when no valid fields provided."""
        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.update_improvement("uuid-123", invalid_field="value")
        assert result is False

    @respx.mock
    def test_delete_improvement_success(self):
        """Should return True on successful delete."""
        route = respx.delete("http://test/improvements/uuid-123").mock(
            return_value=httpx.Response(204)
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.delete_improvement("uuid-123")

        assert result is True
        assert route.called

    @respx.mock
    def test_emit_event_success(self):
        """Should return True on successful event emission."""
        route = respx.post("http://test/improvements/uuid-123/events").mock(
            return_value=httpx.Response(201, json={"uuid": "event-uuid"})
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.emit_improvement_event(
            "uuid-123", "resolved", payload={"reason": "fixed"}
        )

        assert result is True
        assert route.called

    @respx.mock
    def test_emit_event_redacts_payload(self):
        """Should redact sensitive keys in payload."""
        route = respx.post("http://test/improvements/uuid-123/events").mock(
            return_value=httpx.Response(201)
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        client.emit_improvement_event(
            "uuid-123", "action", payload={"api_key": "secret123", "data": "visible"}
        )

        request = route.calls.last.request
        body = request.content.decode()
        assert "secret123" not in body
        assert "[REDACTED]" in body
        assert "visible" in body

    @respx.mock
    def test_sends_auth_header(self):
        """Should send authorization header."""
        route = respx.get("http://test/improvements").mock(
            return_value=httpx.Response(200, json={"improvements": []})
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="secret-token",
            run_uuid="run",
        )
        client.list_improvements()

        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer secret-token"


class TestImprovementsClientErrors:
    """Tests for error handling."""

    @respx.mock
    def test_timeout_returns_empty_list(self):
        """Should return empty list on timeout for list."""
        respx.get("http://test/improvements").mock(
            side_effect=httpx.TimeoutException("timeout")
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
            timeout_ms=100,
        )
        result = client.list_improvements()
        assert result == []

    @respx.mock
    def test_timeout_returns_false_for_create(self):
        """Should return False on timeout for create."""
        respx.post("http://test/improvements").mock(
            side_effect=httpx.TimeoutException("timeout")
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
            timeout_ms=100,
        )
        result = client.create_improvement("Test")
        assert result is False

    @respx.mock
    def test_network_error_returns_false(self):
        """Should return False on network error."""
        respx.post("http://test/improvements").mock(
            side_effect=httpx.ConnectError("connection failed")
        )

        client = ImprovementsClient(
            improvements_url="http://test/improvements",
            run_token="token",
            run_uuid="run",
        )
        result = client.create_improvement("Test")
        assert result is False


class TestGetImprovementsClient:
    """Tests for get_improvements_client helper function."""

    def test_returns_client(self):
        """Should return an ImprovementsClient instance."""
        with patch.dict(os.environ, {}, clear=True):
            client = get_improvements_client()
            assert isinstance(client, ImprovementsClient)

    def test_uses_from_env(self):
        """Should configure from environment."""
        env = {
            "FULCRUM_IMPROVEMENTS_URL": "http://test/improvements",
            "FULCRUM_RUN_TOKEN": "token",
            "FULCRUM_RUN_UUID": "run",
        }
        with patch.dict(os.environ, env, clear=True):
            client = get_improvements_client()
            assert client.enabled is True
