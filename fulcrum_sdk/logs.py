"""Project logs client for Fulcrum v1 APIs."""

from __future__ import annotations

from collections.abc import Sequence

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class LogsResource(BaseResource):
    """Client for project logs v1 endpoints."""

    def list(
        self,
        project_uuid: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        time_preset: str | None = None,
        sources: Sequence[str] | None = None,
        start: str | None = None,
        end: str | None = None,
        statuses: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
        run_uuid: str | None = None,
        ticket_uuid: str | None = None,
        sop_uuid: str | None = None,
        improvement_run_uuid: str | None = None,
        search: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "logs"),
            params=self._clean_params(
                limit=limit,
                cursor=cursor,
                timePreset=time_preset,
                sources=",".join(sources) if sources else None,
                start=start,
                end=end,
                statuses=",".join(statuses) if statuses else None,
                eventTypes=",".join(event_types) if event_types else None,
                runUuid=run_uuid,
                ticketUuid=ticket_uuid,
                sopUuid=sop_uuid,
                improvementRunUuid=improvement_run_uuid,
                search=search,
            ),
        )
