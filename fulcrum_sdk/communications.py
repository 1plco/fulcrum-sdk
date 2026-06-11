"""Project communications client for Fulcrum v1 APIs."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


def _runtime_run_uuid() -> str | None:
    """Resolve the current run UUID from the runtime environment."""
    return (
        os.environ.get("FULCRUM_TEAM_TICKET_RUN_UUID")
        or os.environ.get("FULCRUM_RUN_UUID")
        or None
    )


class CommunicationsResource(BaseResource):
    """Client for project-scoped email communication endpoints."""

    def _bool_param(self, value: bool | None) -> str | None:
        if value is None:
            return None
        return "true" if value else "false"

    def list_threads(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query: str | None = None,
        status: str | None = None,
        classification: str | None = None,
        participant: str | None = None,
        has_attachments: bool | None = None,
        has_pending_drafts: bool | None = None,
        unread: bool | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "communications", "threads"),
            params=self._pagination_params(
                cursor=cursor,
                limit=limit,
                query=query,
                status=status,
                classification=classification,
                participant=participant,
                hasAttachments=self._bool_param(has_attachments),
                hasPendingDrafts=self._bool_param(has_pending_drafts),
                unread=self._bool_param(unread),
            ),
        )

    def search(
        self,
        project_uuid: str,
        query: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
        classification: str | None = None,
        participant: str | None = None,
        has_attachments: bool | None = None,
        has_pending_drafts: bool | None = None,
        unread: bool | None = None,
    ) -> JsonDict:
        return self.list_threads(
            project_uuid,
            cursor=cursor,
            limit=limit,
            query=query,
            status=status,
            classification=classification,
            participant=participant,
            has_attachments=has_attachments,
            has_pending_drafts=has_pending_drafts,
            unread=unread,
        )

    def get_thread(
        self,
        project_uuid: str,
        thread_uuid: str,
        *,
        mode: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "communications",
                "threads",
                thread_uuid,
            ),
            params=self._clean_params(mode=mode),
        )

    def get(self, project_uuid: str, thread_uuid: str, *, mode: str | None = None) -> JsonDict:
        return self.get_thread(project_uuid, thread_uuid, mode=mode)

    def send(
        self,
        project_uuid: str,
        *,
        idempotency_key: str,
        subject: str,
        text: str,
        to: Sequence[str],
        html: str | None = None,
        cc: Sequence[str] | None = None,
        bcc: Sequence[str] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "communications", "threads"),
            json=self._clean_params(
                bcc=list(bcc) if bcc is not None else None,
                bodyHtml=html,
                bodyText=text,
                cc=list(cc) if cc is not None else None,
                idempotencyKey=idempotency_key,
                subject=subject,
                to=list(to),
            ),
        )

    def reply(
        self,
        project_uuid: str,
        thread_uuid: str,
        *,
        idempotency_key: str,
        text: str,
        html: str | None = None,
        subject: str | None = None,
        to: Sequence[str] | None = None,
        cc: Sequence[str] | None = None,
        bcc: Sequence[str] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "communications",
                "threads",
                thread_uuid,
                "reply",
            ),
            json=self._clean_params(
                bcc=list(bcc) if bcc is not None else None,
                bodyHtml=html,
                bodyText=text,
                cc=list(cc) if cc is not None else None,
                idempotencyKey=idempotency_key,
                subject=subject,
                to=list(to) if to is not None else None,
            ),
        )

    def invoke(
        self,
        project_uuid: str,
        thread_uuid: str,
        request: str,
        *,
        idempotency_key: str,
    ) -> JsonDict:
        """Create a project ticket from this thread.

        Requires the ``communication.write`` capability, which runtime tokens
        do not hold; agents should use ``client.tickets.create`` instead.
        ``idempotency_key`` is required by the server (min 8 chars).
        """
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "communications",
                "threads",
                thread_uuid,
                "invoke",
            ),
            json=self._clean_params(
                idempotencyKey=idempotency_key,
                requestText=request,
            ),
        )

    def draft_send(
        self,
        project_uuid: str,
        *,
        subject: str,
        text: str,
        to: Sequence[str],
        blocking: bool = False,
        cc: Sequence[str] | None = None,
        expires_in_days: int | None = None,
        run_uuid: str | None = None,
        ticket_uuid: str | None = None,
    ) -> JsonDict:
        """Create a reviewable outbound draft (new thread).

        With ``blocking=True`` inside a ticket run, the platform stops this
        process and pauses the sandbox before responding — the call may never
        return, and the review outcome arrives in the resume prompt. Without
        ``run_uuid`` a blocking draft cannot pause anything, so it defaults
        from the runtime environment.
        """
        if blocking and run_uuid is None:
            run_uuid = _runtime_run_uuid()
        return self._request(
            "POST",
            self._project_path(project_uuid, "communications", "drafts"),
            json=self._clean_params(
                blocking=blocking,
                bodyText=text,
                cc=list(cc) if cc is not None else None,
                expiresInDays=expires_in_days,
                runUuid=run_uuid,
                subject=subject,
                ticketUuid=ticket_uuid,
                to=list(to),
            ),
        )

    def draft_reply(
        self,
        project_uuid: str,
        thread_uuid: str,
        *,
        text: str,
        blocking: bool = False,
        cc: Sequence[str] | None = None,
        expires_in_days: int | None = None,
        run_uuid: str | None = None,
        subject: str | None = None,
        ticket_uuid: str | None = None,
        to: Sequence[str] | None = None,
    ) -> JsonDict:
        """Create a reviewable reply draft on an existing thread.

        With ``blocking=True`` inside a ticket run, the platform stops this
        process and pauses the sandbox before responding — the call may never
        return, and the review outcome arrives in the resume prompt. Without
        ``run_uuid`` a blocking draft cannot pause anything, so it defaults
        from the runtime environment.
        """
        if blocking and run_uuid is None:
            run_uuid = _runtime_run_uuid()
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "communications",
                "threads",
                thread_uuid,
                "drafts",
            ),
            json=self._clean_params(
                blocking=blocking,
                bodyText=text,
                cc=list(cc) if cc is not None else None,
                expiresInDays=expires_in_days,
                runUuid=run_uuid,
                subject=subject,
                ticketUuid=ticket_uuid,
                to=list(to) if to is not None else None,
            ),
        )

    def await_review(
        self,
        project_uuid: str,
        draft_uuid: str,
        *,
        interval_seconds: float = 2.0,
        timeout_seconds: float = 300.0,
    ) -> JsonDict:
        """Poll a NON-blocking draft until review completes or timeout.

        Never pair this with ``blocking=True`` inside a ticket run: blocking
        drafts kill the calling process and deliver their outcome via the
        resume prompt, so the poll line is unreachable. On timeout the
        still-pending draft is returned unchanged.
        """
        deadline = time.monotonic() + timeout_seconds
        while True:
            draft = self._request(
                "GET",
                self._project_path(
                    project_uuid,
                    "communications",
                    "drafts",
                    draft_uuid,
                ),
            )
            if draft.get("status") != "pending_review":
                return draft
            if time.monotonic() >= deadline:
                return draft
            time.sleep(max(0.1, interval_seconds))
