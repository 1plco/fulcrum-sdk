"""Examples for using the public Fulcrum SDK inside a team-ticket runtime."""

from __future__ import annotations

import time
from typing import Any

from fulcrum_sdk import FulcrumClient

TERMINAL_RUN_STATUSES = {"completed", "failed", "interrupted", "cancelled"}


def list_team_projects(team_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.teams.list_projects(team_uuid)


def load_team_runtime_context(team_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.context(team_uuid)


def list_project_sops(project_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.sops.list(project_uuid)


def check_project_sop_readiness(project_uuid: str, sop_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.sops.readiness(project_uuid, sop_uuid)


def submit_team_graph_for_approval(
    team_uuid: str,
    draft: dict[str, Any],
    *,
    prompt: str | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    graph_result = client.team_runtime.submit_graph(team_uuid, draft)
    graph_uuid = graph_result["graph"]["uuid"]
    return client.team_runtime.request_approval(
        team_uuid,
        graph_uuid=graph_uuid,
        prompt=prompt,
    )


def append_team_graph_event(
    team_uuid: str,
    graph_uuid: str,
    *,
    event_id: str,
    event_type: str,
    status: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.append_graph_event(
        team_uuid,
        graph_uuid,
        event_id=event_id,
        event_type=event_type,
        payload=payload,
        status=status,
    )


def create_team_checkpoint(
    team_uuid: str,
    checkpoint: dict[str, Any],
    *,
    reason: str,
    summary: str,
    graph_uuid: str | None = None,
    sandbox_id: str | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.create_checkpoint(
        team_uuid,
        checkpoint,
        graph_uuid=graph_uuid,
        reason=reason,
        sandbox_id=sandbox_id,
        summary=summary,
    )


def create_team_artifact(
    team_uuid: str,
    *,
    content: dict[str, Any],
    graph_uuid: str,
    kind: str,
    summary: str,
    graph_node_uuid: str | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.create_artifact(
        team_uuid,
        content=content,
        graph_node_uuid=graph_node_uuid,
        graph_uuid=graph_uuid,
        kind=kind,
        summary=summary,
    )


def get_team_artifact(team_uuid: str, artifact_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.get_artifact(team_uuid, artifact_uuid)


def create_team_context_package(
    team_uuid: str,
    node_uuid: str,
    *,
    source_artifact_uuids: list[str] | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.create_context_package(
        team_uuid,
        node_uuid,
        source_artifact_uuids=source_artifact_uuids,
    )


def claim_team_ready_nodes(
    team_uuid: str,
    graph_uuid: str,
    *,
    idempotency_key: str,
    limit: int = 1,
    source_artifact_uuids_by_node_uuid: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.claim_ready_nodes(
        team_uuid,
        graph_uuid,
        idempotency_key=idempotency_key,
        limit=limit,
        source_artifact_uuids_by_node_uuid=source_artifact_uuids_by_node_uuid,
    )


def create_team_node_attempt(
    team_uuid: str,
    node_uuid: str,
    *,
    graph_uuid: str,
    idempotency_key: str,
    source_artifact_uuids: list[str] | None = None,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.create_node_attempt(
        team_uuid,
        node_uuid,
        graph_uuid=graph_uuid,
        idempotency_key=idempotency_key,
        source_artifact_uuids=source_artifact_uuids,
    )


def complete_team_node(
    team_uuid: str,
    node_uuid: str,
    *,
    attempt_uuid: str,
    output_artifact_uuid: str,
    result_summary: str,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_runtime.update_node(
        team_uuid,
        node_uuid,
        attempt_uuid=attempt_uuid,
        output_artifact_uuid=output_artifact_uuid,
        result_summary=result_summary,
        status="completed",
    )


def create_and_execute_project_ticket(project_uuid: str, prompt: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    created = client.tickets.create(project_uuid, prompt)
    ticket = created["ticket"]
    message = created["message"]
    execution = client.tickets.execute(project_uuid, ticket["uuid"], message["uuid"])
    return {"execution": execution, "message": message, "ticket": ticket}


def poll_project_ticket_run(
    project_uuid: str,
    ticket_uuid: str,
    run_uuid: str,
    *,
    interval_seconds: float = 2.0,
    max_attempts: int = 60,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    run: dict[str, Any] = {}
    for _ in range(max_attempts):
        run = client.tickets.get_run(project_uuid, ticket_uuid, run_uuid)
        status = str(run.get("status", "")).lower()
        if status in TERMINAL_RUN_STATUSES:
            return run
        time.sleep(interval_seconds)
    return run


def append_team_ticket_event(
    team_uuid: str,
    team_ticket_uuid: str,
    summary: str,
) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.team_tickets.add_message(
        team_uuid,
        team_ticket_uuid,
        content=summary,
        role="assistant",
    )
