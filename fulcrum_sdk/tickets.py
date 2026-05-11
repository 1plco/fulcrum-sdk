"""Project ticket client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

import httpx

from fulcrum_sdk._internal.http import DEFAULT_TIMEOUT, create_http_client
from fulcrum_sdk.exceptions import FulcrumAPIError, FulcrumConfigError

JsonDict = dict[str, Any]


class TicketsResource:
    """Client for project-scoped ticket v1 endpoints."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        client: Any | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if client is not None:
            self._client = client
            self._api_key = None
            self._base_url = ""
            self._timeout = timeout
            return

        if not base_url:
            raise FulcrumConfigError("base_url is required")

        self._client = None
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def list(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request("GET", f"/api/v1/projects/{project_uuid}/tickets", params=params)

    def create(self, project_uuid: str, prompt: str) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/tickets",
            json={"prompt": prompt},
        )

    def get(self, project_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}",
        )

    def delete(self, project_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}",
        )

    def list_messages(
        self,
        project_uuid: str,
        ticket_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/messages",
            params=params,
        )

    def add_message(self, project_uuid: str, ticket_uuid: str, content: str) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/messages",
            json={"content": content},
        )

    def edit_message(
        self,
        project_uuid: str,
        ticket_uuid: str,
        message_uuid: str,
        content: str,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/messages/{message_uuid}",
            json={"content": content},
        )

    def execute(self, project_uuid: str, ticket_uuid: str, message_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/execute",
            json={"messageUuid": message_uuid},
        )

    def interrupt(self, project_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/interrupt",
        )

    def list_runs(
        self,
        project_uuid: str,
        ticket_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/runs",
            params=params,
        )

    def get_run(self, project_uuid: str, ticket_uuid: str, run_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/runs/{run_uuid}",
        )

    def list_run_events(
        self,
        project_uuid: str,
        ticket_uuid: str,
        run_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/runs/{run_uuid}/events",
            params=params,
        )

    def list_dispatches(
        self,
        project_uuid: str,
        ticket_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/dispatches",
            params=params,
        )

    def list_files(
        self,
        project_uuid: str,
        ticket_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        params = self._pagination_params(cursor=cursor, limit=limit)
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/files",
            params=params,
        )

    def get_file_signed_url(
        self,
        project_uuid: str,
        ticket_uuid: str,
        file_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            f"/api/v1/projects/{project_uuid}/tickets/{ticket_uuid}/files/{file_uuid}/signed-url",
        )

    def get_browser_use_task(
        self,
        project_uuid: str,
        ticket_uuid: str,
        task_id: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            "/api/v1/projects/"
            f"{project_uuid}/tickets/{ticket_uuid}/external-refs/browser-use/tasks/{task_id}",
        )

    def get_phonic_conversation(
        self,
        project_uuid: str,
        ticket_uuid: str,
        conversation_id: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            "/api/v1/projects/"
            f"{project_uuid}/tickets/{ticket_uuid}/external-refs/phonic/conversations/"
            f"{conversation_id}",
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

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, str] | None = None,
    ) -> JsonDict:
        if self._client is not None:
            result = self._client.request(method, path, json=json, params=params)
            if isinstance(result, dict):
                return result
            raise FulcrumAPIError("Expected JSON response from ticket API")

        try:
            with create_http_client(timeout=self._timeout, base_url=self._base_url) as client:
                response = client.request(
                    method,
                    path,
                    headers=self._headers(),
                    json=json,
                    params=params,
                )
        except httpx.HTTPError as exc:
            raise FulcrumAPIError(str(exc)) from exc

        return self._unwrap_response(response)

    def _unwrap_response(self, response: httpx.Response) -> JsonDict:
        try:
            body = response.json()
        except ValueError:
            body = None

        if response.status_code < 200 or response.status_code >= 300:
            message = response.text or f"Fulcrum API returned {response.status_code}"
            if isinstance(body, dict):
                error = body.get("error")
                if isinstance(error, dict) and isinstance(error.get("message"), str):
                    message = error["message"]
                elif isinstance(body.get("message"), str):
                    message = body["message"]
            raise FulcrumAPIError(message, response.status_code)

        if isinstance(body, dict) and body.get("ok") is True:
            data = body.get("data")
            if isinstance(data, dict):
                result = dict(data)
                if isinstance(body.get("meta"), dict):
                    result["meta"] = body["meta"]
                return result
            return {"data": data, **({"meta": body["meta"]} if "meta" in body else {})}

        if isinstance(body, dict):
            return body

        return {"data": body}
