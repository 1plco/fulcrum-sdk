"""Project client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

from fulcrum_sdk.exceptions import FulcrumAPIError
from fulcrum_sdk.models import JsonDict


class ProjectsResource:
    """Client for project-scoped Fulcrum v1 endpoints."""

    def __init__(self, *, client: Any) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request("GET", "/api/v1/projects", params=params)

    def create(
        self,
        *,
        name: str,
        slug: str,
        team_uuid: str | None = None,
    ) -> JsonDict:
        body: JsonDict = {"name": name, "slug": slug}
        if team_uuid is not None:
            body["teamUuid"] = team_uuid
        return self._request("POST", "/api/v1/projects", json=body)

    def get(self, project_uuid: str) -> JsonDict:
        return self._request("GET", f"/api/v1/projects/{project_uuid}")

    def update(self, project_uuid: str, *, name: str, slug: str) -> JsonDict:
        return self._request(
            "PATCH",
            f"/api/v1/projects/{project_uuid}",
            json={"name": name, "slug": slug},
        )

    def delete(self, project_uuid: str) -> JsonDict:
        return self._request("DELETE", f"/api/v1/projects/{project_uuid}")

    def list_members(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/members",
            params=params,
        )

    def add_member(
        self,
        project_uuid: str,
        *,
        clerk_user_id: str,
        role: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/members",
            json={"clerkUserId": clerk_user_id, "role": role},
        )

    def _pagination_params(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, str]:
        params: dict[str, str] = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = str(limit)
        return params

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, str] | None = None,
    ) -> JsonDict:
        result = self._client.request(method, path, json=json, params=params)
        if isinstance(result, dict):
            return result
        raise FulcrumAPIError("Expected JSON response from project API")
