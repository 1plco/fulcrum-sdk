"""Internal DB client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class InternalDbResource(BaseResource):
    """Client for project and team internal DB v1 endpoints."""

    def get(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "internal-db"))

    def schema(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "internal-db/schema"))

    def refresh_schema(self, project_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "internal-db/schema/refresh"),
        )

    def query(self, project_uuid: str, payload: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "internal-db/query"),
            json=payload,
        )

    def table(
        self,
        project_uuid: str,
        table_name: str,
        *,
        columns: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[dict[str, Any]] | None = None,
        sort: dict[str, Any] | None = None,
    ) -> JsonDict:
        return self.query(
            project_uuid,
            self._clean_params(
                tableName=table_name,
                columns=columns,
                limit=limit,
                offset=offset,
                filters=filters,
                sort=sort,
            ),
        )

    def sql(
        self,
        project_uuid: str,
        query: str,
        *,
        parameters: list[Any] | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self.query(
            project_uuid,
            self._clean_params(sql=query, parameters=parameters, limit=limit),
        )

    def team_schema(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "internal-db/schema"))

    def team_query(self, team_uuid: str, payload: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "internal-db/query"),
            json=payload,
        )
