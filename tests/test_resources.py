"""Tests for public v1 resource helpers."""

import httpx
import respx

from fulcrum_sdk import FulcrumClient, ProjectsResource, SopsResource


@respx.mock
def test_projects_resource_lists_projects_with_pagination():
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
    result = client.projects.list(cursor="cursor-1", limit=25)

    assert isinstance(client.projects, ProjectsResource)
    assert result["data"] == [{"uuid": "project-1"}]
    assert route.calls.last.request.url.params["cursor"] == "cursor-1"
    assert route.calls.last.request.url.params["limit"] == "25"


@respx.mock
def test_projects_resource_gets_project_members():
    route = respx.get("http://test/api/v1/projects/project-1/members").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": [{"clerk_user_id": "user-1", "role": "developer"}],
            },
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.projects.list_members("project-1")

    assert result["data"][0]["role"] == "developer"
    assert route.called


@respx.mock
def test_sops_resource_lists_and_gets_sop():
    list_route = respx.get("http://test/api/v1/projects/project-1/sops").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": [{"uuid": "sop-1", "name": "Runbook"}],
            },
        )
    )
    get_route = respx.get("http://test/api/v1/projects/project-1/sops/sop-1").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"uuid": "sop-1", "name": "Runbook"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")

    assert isinstance(client.sops, SopsResource)
    assert client.sops.list("project-1")["data"][0]["uuid"] == "sop-1"
    assert client.sops.get("project-1", "sop-1")["uuid"] == "sop-1"
    assert list_route.called
    assert get_route.called


@respx.mock
def test_sops_resource_requests_parse_stream():
    route = respx.post("http://test/api/v1/projects/project-1/sops/sop-1/parse").mock(
        return_value=httpx.Response(
            200,
            content=b"parsed markdown",
            headers={"content-type": "text/plain"},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    response = client.sops.parse("project-1", "sop-1")

    assert isinstance(response, httpx.Response)
    assert response.read() == b"parsed markdown"
    response.close()
    assert route.called


@respx.mock
def test_tickets_resource_can_stream_execution():
    route = respx.post(
        "http://test/api/v1/projects/project-1/tickets/ticket-1/execute"
    ).mock(
        return_value=httpx.Response(
            202,
            content=b"event: start\n\n",
            headers={"content-type": "text/event-stream"},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    response = client.tickets.execute_stream(
        "project-1",
        "ticket-1",
        "message-1",
        cancel_on_disconnect=True,
    )

    assert isinstance(response, httpx.Response)
    assert response.read() == b"event: start\n\n"
    response.close()
    assert route.calls.last.request.headers["accept"] == "text/event-stream"
    assert route.calls.last.request.headers["x-cancel-on-disconnect"] == "1"
