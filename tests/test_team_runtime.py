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
    graph_read_route = respx.get("http://test/api/v1/teams/team-1/runtime/graphs/graph-1").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "edges": [],
                    "graph": {"uuid": "graph-1"},
                    "nodes": [],
                },
            },
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
    assert client.team_runtime.get_graph("team-1", "graph-1") == {
        "edges": [],
        "graph": {"uuid": "graph-1"},
        "nodes": [],
    }
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
    assert graph_read_route.called
    assert approval_read_route.called


@respx.mock
def test_team_runtime_appends_graph_events():
    route = respx.post("http://test/api/v1/teams/team-1/runtime/graphs/graph-1/events").mock(
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
def test_team_runtime_creates_checkpoints():
    route = respx.post("http://test/api/v1/teams/team-1/runtime/checkpoints").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"checkpoint": {"uuid": "checkpoint-1"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.create_checkpoint(
        "team-1",
        {"step": "approval-wait"},
        graph_uuid="graph-1",
        reason="approval_wait",
        runtime_execution_uuid="runtime-1",
        sandbox_id="sandbox-1",
        summary="Waiting for approval.",
    ) == {"checkpoint": {"uuid": "checkpoint-1"}}
    assert route.calls.last.request.content == (
        b'{"checkpoint":{"step":"approval-wait"},'
        b'"graphUuid":"graph-1",'
        b'"reason":"approval_wait",'
        b'"runtimeExecutionUuid":"runtime-1",'
        b'"sandboxId":"sandbox-1",'
        b'"summary":"Waiting for approval."}'
    )


@respx.mock
def test_team_runtime_creates_and_reads_artifacts():
    create_route = respx.post("http://test/api/v1/teams/team-1/runtime/artifacts").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"artifact": {"uuid": "artifact-1"}}},
        )
    )
    get_route = respx.get("http://test/api/v1/teams/team-1/runtime/artifacts/artifact-1").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"artifact": {"uuid": "artifact-1"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.create_artifact(
        "team-1",
        content={"answer": "ready"},
        graph_uuid="graph-1",
        kind="node_output",
        summary="Ready.",
        artifact_refs=[{"kind": "ticket", "uuid": "ticket-1"}],
        data_classes=["internal"],
        schema_id="answer.v1",
    ) == {"artifact": {"uuid": "artifact-1"}}
    assert client.team_runtime.get_artifact("team-1", "artifact-1") == {
        "artifact": {"uuid": "artifact-1"}
    }
    assert create_route.calls.last.request.content == (
        b'{"artifactRefs":[{"kind":"ticket","uuid":"ticket-1"}],'
        b'"content":{"answer":"ready"},'
        b'"dataClasses":["internal"],'
        b'"graphUuid":"graph-1",'
        b'"kind":"node_output",'
        b'"schemaId":"answer.v1",'
        b'"summary":"Ready."}'
    )
    assert get_route.called


@respx.mock
def test_team_runtime_creates_context_packages():
    route = respx.post("http://test/api/v1/teams/team-1/runtime/nodes/node-1/context-package").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"package": {"uuid": "package-1"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.create_context_package(
        "team-1",
        "node-1",
        source_artifact_uuids=["artifact-1"],
    ) == {"package": {"uuid": "package-1"}}
    assert route.calls.last.request.content == b'{"sourceArtifactUuids":["artifact-1"]}'


@respx.mock
def test_team_runtime_claims_ready_nodes():
    route = respx.post(
        "http://test/api/v1/teams/team-1/runtime/graphs/graph-1/nodes/claim-ready"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"claims": [{"node": {"uuid": "node-1"}}]}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.claim_ready_nodes(
        "team-1",
        "graph-1",
        idempotency_key="claim-1",
        limit=2,
        source_artifact_uuids_by_node_uuid={"node-1": ["artifact-1"]},
    ) == {"claims": [{"node": {"uuid": "node-1"}}]}
    assert route.calls.last.request.content == (
        b'{"idempotencyKey":"claim-1",'
        b'"limit":2,'
        b'"sourceArtifactUuidsByNodeUuid":{"node-1":["artifact-1"]}}'
    )


@respx.mock
def test_team_runtime_updates_nodes():
    route = respx.patch("http://test/api/v1/teams/team-1/runtime/nodes/node-1").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"node": {"status": "completed"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.update_node(
        "team-1",
        "node-1",
        attempt_uuid="attempt-1",
        output_artifact_uuid="artifact-1",
        output_json={"answer": "ready"},
        result_summary="Ready.",
        status="completed",
    ) == {"node": {"status": "completed"}}
    assert route.calls.last.request.content == (
        b'{"attemptUuid":"attempt-1",'
        b'"outputArtifactUuid":"artifact-1",'
        b'"outputJson":{"answer":"ready"},'
        b'"resultSummary":"Ready.",'
        b'"status":"completed"}'
    )


@respx.mock
def test_team_runtime_creates_node_attempts():
    route = respx.post("http://test/api/v1/teams/team-1/runtime/nodes/node-1/attempts").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"claims": [{"attempt": {"uuid": "attempt-1"}}]}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="runtime-token")

    assert client.team_runtime.create_node_attempt(
        "team-1",
        "node-1",
        graph_uuid="graph-1",
        idempotency_key="attempt-1",
        source_artifact_uuids=["artifact-1"],
    ) == {"claims": [{"attempt": {"uuid": "attempt-1"}}]}
    assert route.calls.last.request.content == (
        b'{"graphUuid":"graph-1","idempotencyKey":"attempt-1","sourceArtifactUuids":["artifact-1"]}'
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
