"""Tests for broad v1 SDK resource coverage."""

import httpx
import respx

from fulcrum_sdk import (
    DashboardResource,
    FulcrumClient,
    GithubResource,
    ImprovementsResource,
    InternalDbResource,
    LogsResource,
    OperatorResource,
    ProjectMembersResource,
    ResourcesResource,
    SopSyncResource,
    TeamsResource,
    TeamTicketsResource,
    UnfurlRunsResource,
)


def test_client_exposes_remaining_v1_resources():
    client = FulcrumClient(base_url="http://test", api_key="token")

    assert isinstance(client.project_members, ProjectMembersResource)
    assert isinstance(client.sop_sync, SopSyncResource)
    assert isinstance(client.resources, ResourcesResource)
    assert isinstance(client.improvements, ImprovementsResource)
    assert isinstance(client.unfurl_runs, UnfurlRunsResource)
    assert isinstance(client.github, GithubResource)
    assert isinstance(client.dashboard, DashboardResource)
    assert isinstance(client.logs, LogsResource)
    assert isinstance(client.operator, OperatorResource)
    assert isinstance(client.internal_db, InternalDbResource)
    assert isinstance(client.teams, TeamsResource)
    assert isinstance(client.team_tickets, TeamTicketsResource)


def test_expected_route_groups_have_sdk_properties():
    client = FulcrumClient(base_url="http://test", api_key="token")
    route_groups = {
        "dashboard": client.dashboard,
        "github": client.github,
        "improvement-runs": client.improvements,
        "improvements": client.improvements,
        "internal-db": client.internal_db,
        "logs": client.logs,
        "members": client.project_members,
        "operator": client.operator,
        "resources": client.resources,
        "sop-sync": client.sop_sync,
        "teams": client.teams,
        "team-tickets": client.team_tickets,
        "unfurl-runs": client.unfurl_runs,
    }

    assert set(route_groups) == {
        "dashboard",
        "github",
        "improvement-runs",
        "improvements",
        "internal-db",
        "logs",
        "members",
        "operator",
        "resources",
        "sop-sync",
        "teams",
        "team-tickets",
        "unfurl-runs",
    }


@respx.mock
def test_project_members_resource_updates_and_removes_members():
    update_route = respx.patch(
        "http://test/api/v1/projects/project-1/members/user-1"
    ).mock(return_value=httpx.Response(200, json={"ok": True, "data": {"role": "user"}}))
    delete_route = respx.delete(
        "http://test/api/v1/projects/project-1/members/user-1"
    ).mock(return_value=httpx.Response(200, json={"ok": True, "data": {"deleted": True}}))

    client = FulcrumClient(base_url="http://test", api_key="token")

    assert client.project_members.update("project-1", "user-1", role="user") == {
        "role": "user"
    }
    assert client.project_members.remove("project-1", "user-1") == {"deleted": True}
    assert update_route.calls.last.request.content == b'{"role":"user"}'
    assert delete_route.called


@respx.mock
def test_resources_and_internal_db_routes():
    create_route = respx.post("http://test/api/v1/projects/project-1/resources").mock(
        return_value=httpx.Response(201, json={"ok": True, "data": {"uuid": "res-1"}})
    )
    query_route = respx.post(
        "http://test/api/v1/projects/project-1/internal-db/query"
    ).mock(return_value=httpx.Response(200, json={"ok": True, "data": {"rows": []}}))

    client = FulcrumClient(base_url="http://test", api_key="token")
    created = client.resources.create_sql(
        "project-1",
        name="Warehouse",
        connection_string="postgres://example",
        schema_name="public",
    )
    queried = client.internal_db.sql("project-1", "select 1", parameters=[1])

    assert created["uuid"] == "res-1"
    assert queried["rows"] == []
    assert b'"type":"sql"' in create_route.calls.last.request.content
    assert b'"sql":"select 1"' in query_route.calls.last.request.content


@respx.mock
def test_github_logs_dashboard_and_sop_sync_routes():
    repos_route = respx.get("http://test/api/v1/projects/project-1/github/repos").mock(
        return_value=httpx.Response(200, json={"ok": True, "data": []})
    )
    logs_route = respx.get("http://test/api/v1/projects/project-1/logs").mock(
        return_value=httpx.Response(200, json={"ok": True, "data": {"items": []}})
    )
    costs_route = respx.get("http://test/api/v1/projects/project-1/dashboard/costs").mock(
        return_value=httpx.Response(200, json={"ok": True, "data": {"total": 1}})
    )
    sop_sync_route = respx.post(
        "http://test/api/v1/projects/project-1/sop-sync/pull"
    ).mock(return_value=httpx.Response(200, json={"ok": True, "data": {"pulled": True}}))

    client = FulcrumClient(base_url="http://test", api_key="token")
    assert client.github.list_repositories("project-1", org="acme") == {"data": []}
    assert client.logs.list("project-1", sources=["ticket"], limit=10) == {
        "items": []
    }
    assert client.dashboard.costs("project-1") == {"total": 1}
    assert client.sop_sync.pull("project-1") == {"pulled": True}
    assert repos_route.calls.last.request.url.params["org"] == "acme"
    assert logs_route.calls.last.request.url.params["sources"] == "ticket"
    assert logs_route.calls.last.request.url.params["limit"] == "10"
    assert costs_route.called
    assert sop_sync_route.called


@respx.mock
def test_run_resources_can_stream_or_poll_events():
    improvement_route = respx.post(
        "http://test/api/v1/projects/project-1/improvement-runs"
    ).mock(
        return_value=httpx.Response(
            202,
            content=b"event: start\n\n",
            headers={"content-type": "text/event-stream"},
        )
    )
    unfurl_events_route = respx.get(
        "http://test/api/v1/projects/project-1/unfurl-runs/run-1/events"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": [{"event": "done"}]},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    response = client.improvements.start_run(
        "project-1",
        ["improvement-1"],
        stream=True,
        cancel_on_disconnect=True,
    )
    assert isinstance(response, httpx.Response)
    response.close()
    assert improvement_route.calls.last.request.headers["accept"] == "text/event-stream"
    assert improvement_route.calls.last.request.headers["x-cancel-on-disconnect"] == "1"
    assert client.unfurl_runs.list_events("project-1", "run-1") == {
        "data": [{"event": "done"}]
    }
    assert unfurl_events_route.called


@respx.mock
def test_operator_and_team_ticket_routes():
    operator_route = respx.post(
        "http://test/api/v1/projects/project-1/operator/canvases/canvas-1/builder/plan"
    ).mock(return_value=httpx.Response(200, json={"ok": True, "data": {"run": "run-1"}}))
    team_route = respx.post(
        "http://test/api/v1/teams/team-1/tickets/ticket-1/execute"
    ).mock(
        return_value=httpx.Response(
            202,
            json={"ok": True, "data": {"runUuid": "run-1"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    assert client.operator.plan_canvas_builder("project-1", "canvas-1", {}) == {
        "run": "run-1"
    }
    assert client.team_tickets.execute("team-1", "ticket-1") == {"runUuid": "run-1"}
    assert operator_route.called
    assert team_route.calls.last.request.content == b"{}"


@respx.mock
def test_teams_resource_lists_team_projects():
    route = respx.get("http://test/api/v1/teams/team-1/projects").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": [{"uuid": "project-1"}]},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")

    assert client.teams.list_projects("team-1") == {"data": [{"uuid": "project-1"}]}
    assert route.called
