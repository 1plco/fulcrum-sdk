"""Project membership client for Fulcrum v1 APIs."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class ProjectMembersResource(BaseResource):
    """Client for project membership v1 endpoints."""

    def list(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "members"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def add(self, project_uuid: str, *, clerk_user_id: str, role: str) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "members"),
            json={"clerkUserId": clerk_user_id, "role": role},
        )

    def update(self, project_uuid: str, member_user_id: str, *, role: str) -> JsonDict:
        return self._request(
            "PATCH",
            self._project_path(project_uuid, "members", member_user_id),
            json={"role": role},
        )

    def remove(self, project_uuid: str, member_user_id: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "members", member_user_id),
        )
