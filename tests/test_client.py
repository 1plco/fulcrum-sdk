"""Tests for the public FulcrumClient."""

import os
from unittest.mock import patch

import httpx
import pytest
import respx

from fulcrum_sdk import FulcrumAPIError, FulcrumClient, TicketsResource


def test_client_from_env_reads_runtime_token_and_base_url():
    env = {
        "FULCRUM_API_BASE_URL": "http://test",
        "FULCRUM_RUNTIME_TOKEN": "runtime-token",
    }

    with patch.dict(os.environ, env, clear=True):
        client = FulcrumClient.from_env()

    assert isinstance(client.tickets, TicketsResource)


@respx.mock
def test_client_request_unwraps_success_data_and_sends_auth():
    route = respx.get("http://test/api/v1/projects").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": [{"uuid": "project-1"}],
                "meta": {"hasMore": False},
            },
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.request("GET", "/api/v1/projects")

    assert result == {"data": [{"uuid": "project-1"}], "meta": {"hasMore": False}}
    assert route.calls.last.request.headers["authorization"] == "Bearer token"


@respx.mock
def test_client_request_retries_transient_failures():
    route = respx.get("http://test/api/v1/projects").mock(
        side_effect=[
            httpx.Response(500, json={"ok": False, "error": {"message": "Nope"}}),
            httpx.Response(200, json={"ok": True, "data": {"ok": True}}),
        ]
    )

    client = FulcrumClient(
        base_url="http://test",
        api_key="token",
        retry_delay_seconds=0,
    )
    result = client.request("GET", "/api/v1/projects")

    assert result == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_client_request_raises_structured_api_error():
    respx.get("http://test/api/v1/projects").mock(
        return_value=httpx.Response(
            403,
            json={"ok": False, "error": {"message": "Forbidden"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")

    with pytest.raises(FulcrumAPIError) as exc:
        client.request("GET", "/api/v1/projects")

    assert exc.value.status_code == 403
    assert exc.value.response_body
    assert str(exc.value) == "Forbidden"


@respx.mock
def test_client_request_includes_api_error_details():
    details = {
        "graph": [
            "draft.summary: Too small: expected string to have >=1 characters",
            {"path": ["draft", "nodes", 0, "projectUuid"], "message": "Required"},
        ]
    }
    respx.post("http://test/api/v1/teams/team-1/runtime/graphs").mock(
        return_value=httpx.Response(
            400,
            json={
                "ok": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid graph draft",
                    "details": details,
                },
            },
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")

    with pytest.raises(FulcrumAPIError) as exc:
        client.request("POST", "/api/v1/teams/team-1/runtime/graphs", json={})

    assert exc.value.status_code == 400
    assert exc.value.details == details
    assert str(exc.value) == (
        "Invalid graph draft\n"
        "- graph[0]: draft.summary: Too small: expected string to have >=1 characters\n"
        "- draft.nodes[0].projectUuid: Required"
    )


@respx.mock
def test_tickets_resource_uses_core_client_request():
    route = respx.post("http://test/api/v1/projects/project-1/tickets").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"ticket": {"uuid": "ticket-1"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.tickets.create("project-1", "Run")

    assert result["ticket"]["uuid"] == "ticket-1"
    assert route.called
