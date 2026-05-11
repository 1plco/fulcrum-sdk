"""SOP client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

import httpx

from fulcrum_sdk.exceptions import FulcrumAPIError
from fulcrum_sdk.models import JsonDict


class SopsResource:
    """Client for SOP v1 endpoints."""

    def __init__(self, *, client: Any) -> None:
        self._client = client

    def list(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/sops",
            params=params,
        )

    def create_markdown(self, project_uuid: str, *, name: str, content: str) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/sops",
            json={"name": name, "content": content},
        )

    def create_pdf(
        self,
        project_uuid: str,
        *,
        name: str,
        base64: str,
        size: int,
        current_version: int | None = None,
    ) -> JsonDict:
        body: JsonDict = {
            "file": {
                "name": name,
                "type": "application/pdf",
                "size": size,
                "base64": base64,
            }
        }
        if current_version is not None:
            body["currentVersion"] = current_version
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/sops",
            json=body,
        )

    def get(self, project_uuid: str, sop_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}",
        )

    def rename(self, project_uuid: str, sop_uuid: str, *, name: str) -> JsonDict:
        return self._request(
            "PATCH",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}",
            json={"name": name},
        )

    def delete(self, project_uuid: str, sop_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}",
        )

    def list_versions(self, project_uuid: str, sop_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}/versions",
        )

    def create_version(
        self,
        project_uuid: str,
        sop_uuid: str,
        *,
        content: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}/versions",
            json={"content": content},
        )

    def get_signed_url(self, project_uuid: str, sop_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}/signed-url",
        )

    def parse(
        self,
        project_uuid: str,
        sop_uuid: str,
        *,
        stream: bool = True,
    ) -> JsonDict | httpx.Response:
        return self._client.request(
            "POST",
            f"/api/v1/projects/{project_uuid}/sops/{sop_uuid}/parse",
            json={},
            stream=stream,
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
        raise FulcrumAPIError("Expected JSON response from SOP API")
