"""Shared helpers for Fulcrum v1 resource clients."""

from __future__ import annotations

from typing import Any

import httpx

from fulcrum_sdk.exceptions import FulcrumAPIError
from fulcrum_sdk.models import JsonDict


class BaseResource:
    """Base class for JSON-oriented Fulcrum v1 resource helpers."""

    def __init__(self, *, client: Any) -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonDict:
        result = self._client.request(
            method,
            path,
            json=json,
            params=params,
            headers=headers,
        )
        if isinstance(result, dict):
            return result
        raise FulcrumAPIError("Expected JSON response from Fulcrum API")

    def _stream_request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        result = self._client.request(
            method,
            path,
            json=json,
            params=params,
            headers=headers,
            stream=True,
        )
        if isinstance(result, httpx.Response):
            return result
        raise FulcrumAPIError("Expected streaming response from Fulcrum API")

    def _pagination_params(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        return self._clean_params(cursor=cursor, limit=limit, **extra)

    def _clean_params(self, **values: Any) -> dict[str, Any]:
        return {key: value for key, value in values.items() if value is not None}

    def _project_path(self, project_uuid: str, *segments: str) -> str:
        suffix = "/".join(segment.strip("/") for segment in segments if segment)
        base = f"/api/v1/projects/{project_uuid}"
        return f"{base}/{suffix}" if suffix else base

    def _team_path(self, team_uuid: str, *segments: str) -> str:
        suffix = "/".join(segment.strip("/") for segment in segments if segment)
        base = f"/api/v1/teams/{team_uuid}"
        return f"{base}/{suffix}" if suffix else base
