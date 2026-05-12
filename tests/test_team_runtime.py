"""Tests for team runtime orchestration APIs."""

import httpx
import respx

from fulcrum_sdk import FulcrumClient, TeamRuntimeResource


@respx.mock
def test_team_runtime_context_route():
    route = respx.get("http://test/api/v1/teams/team-1/runtime/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "projects": [{"uuid": "project-1"}],
                    "teamTicketRunUuid": "run-1",
                    "teamTicketUuid": "ticket-1",
                    "teamUuid": "team-1",
                },
            },
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")
    result = client.team_runtime.context("team-1")

    assert result["teamUuid"] == "team-1"
    assert result["projects"] == [{"uuid": "project-1"}]
    assert route.calls.last.request.headers["authorization"] == "Bearer runtime-token"


@respx.mock
def test_team_runtime_graph_and_approval_routes():
    graph_route = respx.post("http://test/api/v1/teams/team-1/runtime/graphs").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"graph": {"uuid": "graph-1"}}},
        )
    )
    approval_route = respx.post("http://test/api/v1/teams/team-1/runtime/approvals").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"approval": {"uuid": "approval-1"}}},
        )
    )
    approval_read_route = respx.get(
        "http://test/api/v1/teams/team-1/runtime/approvals/approval-1"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"status": "pending", "uuid": "approval-1"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")
    draft = {"nodes": [], "summary": "Plan"}

    assert client.team_runtime.submit_graph("team-1", draft) == {"graph": {"uuid": "graph-1"}}
    assert client.team_runtime.request_approval(
        "team-1",
        graph_uuid="graph-1",
        prompt="Please approve",
    ) == {"approval": {"uuid": "approval-1"}}
    assert client.team_runtime.get_approval("team-1", "approval-1") == {
        "status": "pending",
        "uuid": "approval-1",
    }
    assert graph_route.calls.last.request.content == b'{"draft":{"nodes":[],"summary":"Plan"}}'
    assert approval_route.calls.last.request.content == (
        b'{"graphUuid":"graph-1","prompt":"Please approve"}'
    )
    assert approval_read_route.called


@respx.mock
def test_team_runtime_appends_graph_events():
    route = respx.post(
        "http://test/api/v1/teams/team-1/runtime/graphs/graph-1/events"
    ).mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"event": {"uuid": "event-1"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.append_graph_event(
        "team-1",
        "graph-1",
        event_id="planner.step.started",
        event_ts="2026-05-11T00:01:00.000Z",
        event_type="team.graph.planner.step",
        payload={"step": "read-context"},
        status="started",
    ) == {"event": {"uuid": "event-1"}}
    assert route.calls.last.request.content == (
        b'{"eventId":"planner.step.started",'
        b'"eventTs":"2026-05-11T00:01:00.000Z",'
        b'"eventType":"team.graph.planner.step",'
        b'"payload":{"step":"read-context"},'
        b'"status":"started"}'
    )


@respx.mock
def test_sops_resource_reads_readiness():
    route = respx.get("http://test/api/v1/projects/project-1/sops/sop-1/readiness").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"status": "ready"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.sops.readiness("project-1", "sop-1") == {"status": "ready"}
    assert route.called


def test_fulcrum_client_exposes_team_runtime_resource():
    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert isinstance(client.team_runtime, TeamRuntimeResource)
