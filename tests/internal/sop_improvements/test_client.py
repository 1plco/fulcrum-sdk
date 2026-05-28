"""Tests for SopImprovementsClient."""

import os
from unittest.mock import patch

import httpx
import respx

from fulcrum_sdk._internal.sop_improvements import (
    SopImprovementsClient,
    get_sop_improvements_client,
)


class TestSopImprovementsClientFromEnv:
    def test_from_env_with_all_vars(self):
        env = {
            "FULCRUM_SOP_IMPROVEMENTS_URL": "http://localhost:3000/api/sop-improvements",
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_PROJECT_UUID": "project-123",
            "FULCRUM_TICKET_UUID": "ticket-123",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = SopImprovementsClient.from_env()
            assert client.enabled is True

    def test_from_env_missing_url(self):
        env = {
            "FULCRUM_RUN_TOKEN": "test-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = SopImprovementsClient.from_env()
            assert client.enabled is False

    def test_from_env_falls_back_to_dispatch_token(self):
        env = {
            "FULCRUM_SOP_IMPROVEMENTS_URL": "http://localhost:3000/api/sop-improvements",
            "FULCRUM_DISPATCH_TOKEN": "fallback-token",
            "FULCRUM_RUN_UUID": "run-456",
        }
        with patch.dict(os.environ, env, clear=True):
            client = SopImprovementsClient.from_env()
            assert client.enabled is True
            assert client._run_token == "fallback-token"


class TestSopImprovementsClientOperations:
    def test_noop_methods_are_best_effort(self):
        client = SopImprovementsClient()
        assert client.list_sop_improvements() == []
        assert client.create_sop_improvement("Clarify approval rule") is False

    @respx.mock
    def test_list_sop_improvements_success(self):
        route = respx.get("http://test/sop-improvements").mock(
            return_value=httpx.Response(
                200,
                json={
                    "sop_improvements": [
                        {
                            "uuid": "sop-imp-1",
                            "project_uuid": "project",
                            "title": "Clarify approval rule",
                            "status": "open",
                        }
                    ]
                },
            )
        )

        client = SopImprovementsClient(
            sop_improvements_url="http://test/sop-improvements",
            run_token="token",
            project_uuid="project",
            run_uuid="run",
        )
        result = client.list_sop_improvements(status="open")

        assert len(result) == 1
        assert result[0].uuid == "sop-imp-1"
        assert route.called
        assert route.calls.last.request.headers["authorization"] == "Bearer token"
        assert "status=open" in str(route.calls.last.request.url)

    @respx.mock
    def test_create_sop_improvement_success(self):
        route = respx.post("http://test/sop-improvements").mock(
            return_value=httpx.Response(201, json={"uuid": "sop-imp-1"})
        )

        client = SopImprovementsClient(
            sop_improvements_url="http://test/sop-improvements",
            run_token="token",
            project_uuid="project",
            ticket_uuid="ticket",
            run_uuid="run",
        )
        result = client.create_sop_improvement(
            "Clarify approval rule",
            observed_gap="SOP does not specify who approves negative totals.",
            suggested_change="Add finance-manager approval for negative totals.",
            section_anchor="Validation",
            dedupe_key="validation-negative-total-approval",
        )

        assert result is True
        assert route.called
        body = route.calls.last.request.content.decode()
        assert "Clarify approval rule" in body
        assert "run" in body
        assert "ticket" in body

    @respx.mock
    def test_create_sop_improvement_returns_false_on_server_error(self):
        respx.post("http://test/sop-improvements").mock(return_value=httpx.Response(500))

        client = SopImprovementsClient(
            sop_improvements_url="http://test/sop-improvements",
            run_token="token",
            run_uuid="run",
        )

        assert client.create_sop_improvement("Clarify approval rule") is False


class TestGetSopImprovementsClient:
    def test_returns_client(self):
        with patch.dict(os.environ, {}, clear=True):
            client = get_sop_improvements_client()
            assert isinstance(client, SopImprovementsClient)
