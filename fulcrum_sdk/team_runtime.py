"""Team runtime client for Fulcrum v1 orchestration endpoints."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class TeamRuntimeResource(BaseResource):
    """Client for team-ticket runtime-only orchestration endpoints."""

    def context(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "runtime", "context"))

    def submit_graph(self, team_uuid: str, draft: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs"),
            json={"draft": draft},
        )

    def request_approval(
        self,
        team_uuid: str,
        *,
        graph_uuid: str,
        prompt: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "approvals"),
            json=self._clean_params(graphUuid=graph_uuid, prompt=prompt),
        )

    def get_approval(self, team_uuid: str, approval_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "runtime", "approvals", approval_uuid),
        )

    def append_graph_event(
        self,
        team_uuid: str,
        graph_uuid: str,
        *,
        event_id: str,
        event_type: str,
        status: str,
        event_ts: str | None = None,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs", graph_uuid, "events"),
            json=self._clean_params(
                eventId=event_id,
                eventTs=event_ts,
                eventType=event_type,
                payload=payload,
                status=status,
            ),
        )
