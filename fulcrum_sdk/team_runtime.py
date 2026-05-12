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
