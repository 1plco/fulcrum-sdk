"""Tests for GuidanceClient."""

import os
from unittest.mock import patch

import httpx
import respx

from fulcrum_sdk._internal.guidance import (
    GuidanceClient,
    GuidanceRequested,
    GuidanceRequestResult,
    get_guidance_client,
)


class TestGuidanceClientFromEnv:
    def test_from_env_with_all_vars(self):
        env = {
            "FULCRUM_GUIDANCE_URL": "http://localhost:3000/api/guidance",
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_PROJECT_UUID": "project-123",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
            "FULCRUM_MESSAGE_UUID": "message-789",
        }
        with patch.dict(os.environ, env, clear=True):
            client = GuidanceClient.from_env()
            assert client.enabled is True

    def test_from_env_missing_url(self):
        env = {
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = GuidanceClient.from_env()
            assert client.enabled is False

    def test_from_env_prefers_run_token(self):
        env = {
            "FULCRUM_GUIDANCE_URL": "http://localhost:3000/api/guidance",
            "FULCRUM_RUN_TOKEN": "preferred-token",
            "FULCRUM_DISPATCH_TOKEN": "deprecated-token",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = GuidanceClient.from_env()
            assert client.enabled is True
            assert client._run_token == "preferred-token"


class TestGuidanceClientOperations:
    def test_noop_seek_guidance_returns_false(self):
        client = GuidanceClient()
        assert client.seek_guidance("What should I do?") is False

    @respx.mock
    def test_seek_guidance_raises_after_acceptance(self):
        route = respx.post("http://test/guidance").mock(
            return_value=httpx.Response(
                202,
                json={
                    "requestUuid": "guidance-123",
                    "status": "pending",
                },
            )
        )

        client = GuidanceClient(
            guidance_url="http://test/guidance",
            run_token="token",
            project_uuid="project",
            ticket_uuid="ticket",
            run_uuid="run",
            message_uuid="message",
        )

        try:
            client.seek_guidance(
                "The SOP does not cover negative invoice totals.",
                sop_section="Validation",
                context={"api_key": "secret", "invoice_id": "inv-1"},
            )
        except GuidanceRequested as exc:
            assert exc.result.request_uuid == "guidance-123"
        else:
            raise AssertionError("Expected GuidanceRequested")

        assert route.called
        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer token"
        body = request.content.decode()
        assert "negative invoice totals" in body
        assert "Validation" in body
        assert "secret" not in body
        assert "[REDACTED]" in body
        assert "message" in body

    @respx.mock
    def test_seek_guidance_can_return_result_without_raising(self):
        respx.post("http://test/guidance").mock(
            return_value=httpx.Response(
                200,
                json={"guidance_request": {"uuid": "guidance-123", "status": "pending"}},
            )
        )

        client = GuidanceClient(
            guidance_url="http://test/guidance",
            run_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )

        result = client.seek_guidance(
            "The SOP is missing a required approval rule.",
            raise_on_accept=False,
        )

        assert isinstance(result, GuidanceRequestResult)
        assert result.request_uuid == "guidance-123"

    @respx.mock
    def test_seek_guidance_returns_false_on_server_error(self):
        respx.post("http://test/guidance").mock(return_value=httpx.Response(500))

        client = GuidanceClient(
            guidance_url="http://test/guidance",
            run_token="token",
            ticket_uuid="ticket",
            run_uuid="run",
        )

        assert client.seek_guidance("What should I do?") is False


class TestGetGuidanceClient:
    def test_returns_client(self):
        with patch.dict(os.environ, {}, clear=True):
            client = get_guidance_client()
            assert isinstance(client, GuidanceClient)
