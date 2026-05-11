"""Tests for public ticket APIs."""

import httpx
import pytest
import respx

from fulcrum_sdk import FulcrumClient, TicketsResource
from fulcrum_sdk.exceptions import FulcrumAPIError


@respx.mock
def test_tickets_resource_creates_ticket():
    route = respx.post("http://test/api/v1/projects/project-1/tickets").mock(
        return_value=httpx.Response(
            201,
            json={
                "ok": True,
                "data": {
                    "message": {"uuid": "message-1"},
                    "ticket": {"uuid": "ticket-1"},
                },
            },
        )
    )

    tickets = TicketsResource(base_url="http://test", api_key="token")
    result = tickets.create("project-1", "Run the SOP")

    assert result["ticket"]["uuid"] == "ticket-1"
    assert route.calls.last.request.headers["authorization"] == "Bearer token"
    assert route.calls.last.request.content == b'{"prompt":"Run the SOP"}'


@respx.mock
def test_tickets_resource_executes_ticket():
    route = respx.post(
        "http://test/api/v1/projects/project-1/tickets/ticket-1/execute"
    ).mock(
        return_value=httpx.Response(
            202,
            json={
                "ok": True,
                "data": {
                    "assistantMessageUuid": "assistant-1",
                    "runUuid": "run-1",
                },
            },
        )
    )

    tickets = TicketsResource(base_url="http://test", api_key="token")
    result = tickets.execute("project-1", "ticket-1", "message-1")

    assert result["runUuid"] == "run-1"
    assert route.calls.last.request.content == b'{"messageUuid":"message-1"}'


@respx.mock
def test_tickets_resource_reads_run_events_with_pagination():
    route = respx.get(
        "http://test/api/v1/projects/project-1/tickets/ticket-1/runs/run-1/events"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": [{"event_id": "event-1"}],
                "meta": {"hasMore": False},
            },
        )
    )

    tickets = TicketsResource(base_url="http://test", api_key="token")
    result = tickets.list_run_events(
        "project-1",
        "ticket-1",
        "run-1",
        cursor="cursor-1",
        limit=20,
    )

    assert result["data"] == [{"event_id": "event-1"}]
    assert result["meta"] == {"hasMore": False}
    assert route.calls.last.request.url.params["cursor"] == "cursor-1"
    assert route.calls.last.request.url.params["limit"] == "20"


@respx.mock
def test_tickets_resource_raises_api_errors():
    respx.get("http://test/api/v1/projects/project-1/tickets/ticket-1").mock(
        return_value=httpx.Response(
            404,
            json={
                "ok": False,
                "error": {"code": "NOT_FOUND", "message": "Ticket not found"},
            },
        )
    )

    tickets = TicketsResource(base_url="http://test", api_key="token")

    with pytest.raises(FulcrumAPIError) as exc:
        tickets.get("project-1", "ticket-1")

    assert exc.value.status_code == 404
    assert str(exc.value) == "Ticket not found"


def test_fulcrum_client_exposes_tickets_resource():
    client = FulcrumClient(base_url="http://test", api_key="token")

    assert isinstance(client.tickets, TicketsResource)
