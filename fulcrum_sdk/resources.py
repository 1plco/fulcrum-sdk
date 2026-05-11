"""Project resource client for Fulcrum v1 APIs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class ResourcesResource(BaseResource):
    """Client for project resource v1 endpoints."""

    def list(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "resources"))

    def create(self, project_uuid: str, payload: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "resources"),
            json=payload,
        )

    def create_file(
        self,
        project_uuid: str,
        *,
        name: str,
        files: Sequence[dict[str, Any]],
        description: str | None = None,
    ) -> JsonDict:
        return self.create(
            project_uuid,
            {
                "type": "file",
                "name": name,
                "files": files,
                **({"description": description} if description is not None else {}),
            },
        )

    def create_sql(
        self,
        project_uuid: str,
        *,
        name: str,
        connection_string: str,
        description: str | None = None,
        schema_name: str | None = None,
    ) -> JsonDict:
        return self.create(
            project_uuid,
            self._clean_params(
                type="sql",
                name=name,
                description=description,
                connectionString=connection_string,
                schemaName=schema_name,
            ),
        )

    def create_secret(
        self,
        project_uuid: str,
        *,
        name: str,
        secrets: Sequence[dict[str, str]],
        description: str | None = None,
    ) -> JsonDict:
        return self.create(
            project_uuid,
            {
                "type": "secret",
                "name": name,
                "secrets": secrets,
                **({"description": description} if description is not None else {}),
            },
        )

    def get(self, project_uuid: str, resource_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "resources", resource_uuid),
        )

    def update(
        self,
        project_uuid: str,
        resource_uuid: str,
        *,
        name: str,
        description: str | None = None,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._project_path(project_uuid, "resources", resource_uuid),
            json=self._clean_params(name=name, description=description),
        )

    def delete(self, project_uuid: str, resource_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "resources", resource_uuid),
        )

    def add_files(
        self,
        project_uuid: str,
        resource_uuid: str,
        *,
        files: Sequence[dict[str, Any]],
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "resources", resource_uuid, "files"),
            json={"files": files},
        )

    def delete_file(
        self,
        project_uuid: str,
        resource_uuid: str,
        file_uuid: str,
    ) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(
                project_uuid,
                "resources",
                resource_uuid,
                "files",
                file_uuid,
            ),
        )

    def get_file_signed_url(
        self,
        project_uuid: str,
        resource_uuid: str,
        file_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "resources",
                resource_uuid,
                "files",
                file_uuid,
                "signed-url",
            ),
        )

    def refresh_schema(
        self,
        project_uuid: str,
        resource_uuid: str,
        *,
        schema_name: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "resources", resource_uuid, "refresh-schema"),
            json=self._clean_params(schemaName=schema_name),
        )

    def sync_env(self, project_uuid: str, *, push_to_github: bool | None = None) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "env-sync"),
            json=self._clean_params(pushToGitHub=push_to_github),
        )
