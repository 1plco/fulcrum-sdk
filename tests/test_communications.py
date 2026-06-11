"""Tests for project communication APIs."""

import json

import httpx
import respx

from fulcrum_sdk import CommunicationsResource, FulcrumClient


@respx.mock
def test_communications_lists_and_searches_threads():
    list_route = respx.get("http://test/api/v1/projects/project-1/communications/threads").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "data": [{"uuid": "thread-1"}],
                "meta": {"hasMore": False},
            },
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.list_threads(
        "project-1",
        classification="trusted",
        cursor="cursor-1",
        has_attachments=True,
        has_pending_drafts=False,
        limit=25,
        participant="customer@example.com",
        query="invoice",
        status="open",
        unread=True,
    )

    assert isinstance(client.communications, CommunicationsResource)
    assert result["data"] == [{"uuid": "thread-1"}]
    params = list_route.calls.last.request.url.params
    assert params["classification"] == "trusted"
    assert params["cursor"] == "cursor-1"
    assert params["hasAttachments"] == "true"
    assert params["hasPendingDrafts"] == "false"
    assert params["limit"] == "25"
    assert params["participant"] == "customer@example.com"
    assert params["query"] == "invoice"
    assert params["status"] == "open"
    assert params["unread"] == "true"

    client.communications.search("project-1", "receipt", limit=10)
    search_params = list_route.calls.last.request.url.params
    assert search_params["query"] == "receipt"
    assert search_params["limit"] == "10"


@respx.mock
def test_communications_gets_thread_with_mode():
    route = respx.get(
        "http://test/api/v1/projects/project-1/communications/threads/thread-1"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"uuid": "thread-1", "messages": []}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.get_thread("project-1", "thread-1", mode="summary")

    assert result["uuid"] == "thread-1"
    assert route.calls.last.request.url.params["mode"] == "summary"


@respx.mock
def test_communications_sends_without_sender_or_attachments():
    route = respx.post("http://test/api/v1/projects/project-1/communications/threads").mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"messageUuid": "message-1"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.send(
        "project-1",
        bcc=["audit@example.com"],
        cc=["ops@example.com"],
        html="<p>Hello</p>",
        idempotency_key="send-1",
        subject="Invoice",
        text="Hello",
        to=["customer@example.com"],
    )

    payload = json.loads(route.calls.last.request.content)
    assert result == {"messageUuid": "message-1"}
    assert payload == {
        "bcc": ["audit@example.com"],
        "bodyHtml": "<p>Hello</p>",
        "bodyText": "Hello",
        "cc": ["ops@example.com"],
        "idempotencyKey": "send-1",
        "subject": "Invoice",
        "to": ["customer@example.com"],
    }
    assert "from" not in payload
    assert "attachments" not in payload


@respx.mock
def test_communications_replies_to_thread():
    route = respx.post(
        "http://test/api/v1/projects/project-1/communications/threads/thread-1/reply"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "data": {"messageUuid": "message-2"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.reply(
        "project-1",
        "thread-1",
        idempotency_key="reply-1",
        subject="Re: Invoice",
        text="Thanks",
    )

    assert result == {"messageUuid": "message-2"}
    assert json.loads(route.calls.last.request.content) == {
        "bodyText": "Thanks",
        "idempotencyKey": "reply-1",
        "subject": "Re: Invoice",
    }


@respx.mock
def test_communications_invokes_ticket_from_thread():
    route = respx.post(
        "http://test/api/v1/projects/project-1/communications/threads/thread-1/invoke"
    ).mock(
        return_value=httpx.Response(
            202,
            json={"ok": True, "data": {"ticketUuid": "ticket-1"}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.invoke(
        "project-1",
        "thread-1",
        "Reconcile this invoice",
        idempotency_key="invoke-1",
    )

    assert result == {"ticketUuid": "ticket-1"}
    # Wire contract: the server schema requires requestText (the `request`
    # key would be stripped by zod and the call would 400).
    assert json.loads(route.calls.last.request.content) == {
        "idempotencyKey": "invoke-1",
        "requestText": "Reconcile this invoice",
    }


@respx.mock
def test_communications_creates_send_and_reply_drafts():
    send_route = respx.post(
        "http://test/api/v1/projects/project-1/communications/drafts"
    ).mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"draft": {"uuid": "draft-send"}}},
        )
    )
    reply_route = respx.post(
        "http://test/api/v1/projects/project-1/communications/threads/thread-1/drafts"
    ).mock(
        return_value=httpx.Response(
            201,
            json={"ok": True, "data": {"draft": {"uuid": "draft-reply"}}},
        )
    )

    client = FulcrumClient(base_url="http://test", api_key="token")
    send_result = client.communications.draft_send(
        "project-1",
        blocking=True,
        cc=["ops@example.com"],
        expires_in_days=3,
        run_uuid="run-1",
        subject="Invoice",
        text="Please review this invoice.",
        ticket_uuid="ticket-1",
        to=["customer@example.com"],
    )
    reply_result = client.communications.draft_reply(
        "project-1",
        "thread-1",
        blocking=True,
        text="Thanks, we will reconcile this.",
    )

    assert send_result["draft"]["uuid"] == "draft-send"
    assert json.loads(send_route.calls.last.request.content) == {
        "blocking": True,
        "bodyText": "Please review this invoice.",
        "cc": ["ops@example.com"],
        "expiresInDays": 3,
        "runUuid": "run-1",
        "subject": "Invoice",
        "ticketUuid": "ticket-1",
        "to": ["customer@example.com"],
    }
    assert reply_result["draft"]["uuid"] == "draft-reply"
    assert json.loads(reply_route.calls.last.request.content) == {
        "blocking": True,
        "bodyText": "Thanks, we will reconcile this.",
    }


@respx.mock
def test_communications_awaits_draft_review(monkeypatch):
    route = respx.get(
        "http://test/api/v1/projects/project-1/communications/drafts/draft-1"
    ).mock(
        side_effect=[
            httpx.Response(
                200,
                json={"ok": True, "data": {"status": "pending_review"}},
            ),
            httpx.Response(
                200,
                json={"ok": True, "data": {"status": "approved_sent"}},
            ),
        ]
    )
    monkeypatch.setattr("time.sleep", lambda _seconds: None)

    client = FulcrumClient(base_url="http://test", api_key="token")
    result = client.communications.await_review(
        "project-1",
        "draft-1",
        interval_seconds=0.1,
        timeout_seconds=1,
    )

    assert result["status"] == "approved_sent"
    assert route.call_count == 2
