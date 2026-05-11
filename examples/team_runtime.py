"""Examples for using the public Fulcrum SDK inside a team-ticket runtime."""

from __future__ import annotations

import time
from typing import Any

from fulcrum_sdk import FulcrumClient

TERMINAL_RUN_STATUSES = {"completed", "failed", "interrupted", "cancelled"}


def list_team_projects(team_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.teams.list_projects(team_uuid)


def list_project_sops(project_uuid: str) -> dict[str, Any]:
    client = FulcrumClient.from_env()
    return client.sops.list(project_uuid)


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
