"""Team client for Fulcrum v1 APIs."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class TeamsResource(BaseResource):
    """Client for team v1 endpoints."""

    def list(self) -> JsonDict:
        return self._request("GET", "/api/v1/teams")

    def get(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid))

    def list_members(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "members"))

    def add_member(self, team_uuid: str, *, clerk_user_id: str, role: str) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "members"),
            json={"clerkUserId": clerk_user_id, "role": role},
        )

    def update_member(self, team_uuid: str, member_user_id: str, *, role: str) -> JsonDict:
        return self._request(
            "PATCH",
            self._team_path(team_uuid, "members", member_user_id),
            json={"role": role},
        )

    def remove_member(self, team_uuid: str, member_user_id: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._team_path(team_uuid, "members", member_user_id),
        )

    def list_projects(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "projects"))

    def add_project(
        self,
        team_uuid: str,
        *,
        project_uuid: str,
        is_primary: bool | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "projects"),
            json=self._clean_params(projectUuid=project_uuid, isPrimary=is_primary),
        )

    def remove_project(self, team_uuid: str, project_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._team_path(team_uuid, "projects", project_uuid),
        )
