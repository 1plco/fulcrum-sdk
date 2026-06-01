"""User-facing Fulcrum client."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import httpx

from fulcrum_sdk._internal.http import DEFAULT_TIMEOUT, create_http_client
from fulcrum_sdk.dashboard import DashboardResource
from fulcrum_sdk.exceptions import FulcrumAPIError, FulcrumConfigError
from fulcrum_sdk.github import GithubResource
from fulcrum_sdk.improvements import ImprovementsResource
from fulcrum_sdk.internal_db import InternalDbResource
from fulcrum_sdk.logs import LogsResource
from fulcrum_sdk.models import JsonDict
from fulcrum_sdk.operator import OperatorResource
from fulcrum_sdk.project_members import ProjectMembersResource
from fulcrum_sdk.projects import ProjectsResource
from fulcrum_sdk.resources import ResourcesResource
from fulcrum_sdk.sop_sync import SopSyncResource
from fulcrum_sdk.sops import SopsResource
from fulcrum_sdk.team_runtime import TeamRuntimeResource
from fulcrum_sdk.team_tickets import TeamTicketsResource
from fulcrum_sdk.teams import TeamsResource
from fulcrum_sdk.tickets import TicketsResource
from fulcrum_sdk.unfurl_runs import UnfurlRunsResource

DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_DELAY_SECONDS = 0.25


class FulcrumClient:
    """Client for Fulcrum public v1 APIs."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        resolved_base_url = (
            base_url
            or os.environ.get("FULCRUM_API_BASE_URL")
            or os.environ.get("FULCRUM_BASE_URL")
        )
        if not resolved_base_url:
            raise FulcrumConfigError(
                "base_url, FULCRUM_API_BASE_URL, or FULCRUM_BASE_URL is required"
            )

        self._api_key = (
            api_key
            or os.environ.get("FULCRUM_API_KEY")
            or os.environ.get("FULCRUM_RUNTIME_TOKEN")
            or os.environ.get("FULCRUM_RUN_TOKEN")
        )
        self._base_url = resolved_base_url.rstrip("/")
        self._max_retries = max(0, max_retries)
        self._retry_delay_seconds = max(0.0, retry_delay_seconds)
        self._timeout = timeout
        self._dashboard: DashboardResource | None = None
        self._github: GithubResource | None = None
        self._improvements: ImprovementsResource | None = None
        self._internal_db: InternalDbResource | None = None
        self._logs: LogsResource | None = None
        self._operator: OperatorResource | None = None
        self._project_members: ProjectMembersResource | None = None
        self._projects: ProjectsResource | None = None
        self._resources: ResourcesResource | None = None
        self._sop_sync: SopSyncResource | None = None
        self._sops: SopsResource | None = None
        self._team_runtime: TeamRuntimeResource | None = None
        self._team_tickets: TeamTicketsResource | None = None
        self._teams: TeamsResource | None = None
        self._tickets: TicketsResource | None = None
        self._unfurl_runs: UnfurlRunsResource | None = None

    @classmethod
    def from_env(cls) -> FulcrumClient:
        """Create a client from Fulcrum API base URL and bearer-token env vars."""
        return cls()

    @property
    def tickets(self) -> TicketsResource:
        if self._tickets is None:
            self._tickets = TicketsResource(client=self)
        return self._tickets

    @property
    def projects(self) -> ProjectsResource:
        if self._projects is None:
            self._projects = ProjectsResource(client=self)
        return self._projects

    @property
    def sops(self) -> SopsResource:
        if self._sops is None:
            self._sops = SopsResource(client=self)
        return self._sops

    @property
    def project_members(self) -> ProjectMembersResource:
        if self._project_members is None:
            self._project_members = ProjectMembersResource(client=self)
        return self._project_members

    @property
    def sop_sync(self) -> SopSyncResource:
        if self._sop_sync is None:
            self._sop_sync = SopSyncResource(client=self)
        return self._sop_sync

    @property
    def resources(self) -> ResourcesResource:
        if self._resources is None:
            self._resources = ResourcesResource(client=self)
        return self._resources

    @property
    def improvements(self) -> ImprovementsResource:
        if self._improvements is None:
            self._improvements = ImprovementsResource(client=self)
        return self._improvements

    @property
    def unfurl_runs(self) -> UnfurlRunsResource:
        if self._unfurl_runs is None:
            self._unfurl_runs = UnfurlRunsResource(client=self)
        return self._unfurl_runs

    @property
    def github(self) -> GithubResource:
        if self._github is None:
            self._github = GithubResource(client=self)
        return self._github

    @property
    def dashboard(self) -> DashboardResource:
        if self._dashboard is None:
            self._dashboard = DashboardResource(client=self)
        return self._dashboard

    @property
    def logs(self) -> LogsResource:
        if self._logs is None:
            self._logs = LogsResource(client=self)
        return self._logs

    @property
    def operator(self) -> OperatorResource:
        if self._operator is None:
            self._operator = OperatorResource(client=self)
        return self._operator

    @property
    def internal_db(self) -> InternalDbResource:
        if self._internal_db is None:
            self._internal_db = InternalDbResource(client=self)
        return self._internal_db

    @property
    def team_tickets(self) -> TeamTicketsResource:
        if self._team_tickets is None:
            self._team_tickets = TeamTicketsResource(client=self)
        return self._team_tickets

    @property
    def team_runtime(self) -> TeamRuntimeResource:
        if self._team_runtime is None:
            self._team_runtime = TeamRuntimeResource(client=self)
        return self._team_runtime

    @property
    def teams(self) -> TeamsResource:
        if self._teams is None:
            self._teams = TeamsResource(client=self)
        return self._teams

    def request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        stream: bool = False,
    ) -> JsonDict | httpx.Response:
        """Call a Fulcrum v1 API path.

        Args:
            method: HTTP method.
            path: Absolute API path such as /api/v1/projects.
            json: Optional JSON request body.
            params: Optional query parameters.
            headers: Optional per-request headers.
            stream: When true, return the raw response for caller-managed streaming.

        Returns:
            Unwrapped response data for JSON routes, or a raw response for streams.
        """
        if stream:
            return self._stream_request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
            )

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                with self._client() as client:
                    response = client.request(
                        method,
                        path,
                        headers=self._headers(headers),
                        json=json,
                        params=params,
                    )
                if self._should_retry(response) and attempt < self._max_retries:
                    self._sleep_before_retry(attempt)
                    continue
                return self._unwrap_response(response)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise FulcrumAPIError(str(exc)) from exc
                self._sleep_before_retry(attempt)

        raise FulcrumAPIError(str(last_error) if last_error else "Request failed")

    @contextmanager
    def _client(self) -> Iterator[httpx.Client]:
        with create_http_client(timeout=self._timeout, base_url=self._base_url) as client:
            yield client

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        if extra:
            headers.update(extra)
        return headers

    def _stream_request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        client = create_http_client(timeout=self._timeout, base_url=self._base_url)
        response = client.build_request(
            method,
            path,
            headers=self._headers(headers),
            json=json,
            params=params,
        )
        stream = client.send(response, stream=True)
        if stream.status_code < 200 or stream.status_code >= 300:
            body = stream.read().decode(errors="replace")
            client.close()
            raise self._api_error(stream.status_code, body)
        return stream

    def _sleep_before_retry(self, attempt: int) -> None:
        if self._retry_delay_seconds <= 0:
            return
        time.sleep(self._retry_delay_seconds * (2**attempt))

    def _should_retry(self, response: httpx.Response) -> bool:
        return response.status_code == 429 or response.status_code >= 500

    def _unwrap_response(self, response: httpx.Response) -> JsonDict:
        body_text = response.text
        if response.status_code < 200 or response.status_code >= 300:
            raise self._api_error(response.status_code, body_text)

        try:
            body = response.json()
        except ValueError:
            return {"data": body_text}

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

    def _api_error(self, status_code: int, body_text: str) -> FulcrumAPIError:
        snippet = body_text[:500]
        message = f"Fulcrum API returned {status_code}"
        details: Any | None = None
        try:
            body = httpx.Response(status_code, content=body_text).json()
        except ValueError:
            body = None

        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict):
                if isinstance(error.get("message"), str):
                    message = error["message"]
                details = error.get("details")
            elif isinstance(body.get("message"), str):
                message = body["message"]
            if details is None:
                details = body.get("details")

        details_message = self._format_error_details(details)
        if details_message and details_message not in message:
            message = f"{message}\n{details_message}"

        return FulcrumAPIError(message, status_code, snippet, details)

    def _format_error_details(self, details: Any) -> str | None:
        if details is None:
            return None

        if isinstance(details, dict):
            lines = [
                line
                for key, value in details.items()
                for line in self._iter_error_detail_lines(value, str(key))
            ]
        else:
            lines = list(self._iter_error_detail_lines(details, "details"))

        if not lines:
            return None

        max_lines = 12
        if len(lines) > max_lines:
            remaining = len(lines) - max_lines
            lines = lines[:max_lines] + [f"- ... {remaining} more detail(s)"]

        return "\n".join(lines)

    def _iter_error_detail_lines(self, value: Any, path: str) -> Iterator[str]:
        if isinstance(value, str):
            yield f"- {path}: {value}"
            return

        if isinstance(value, list):
            for index, item in enumerate(value):
                item_path = f"{path}[{index}]"
                if isinstance(item, dict) and isinstance(item.get("message"), str):
                    issue_path = self._format_issue_path(item.get("path"))
                    yield f"- {issue_path or item_path}: {item['message']}"
                    continue
                yield from self._iter_error_detail_lines(item, item_path)
            return

        if isinstance(value, dict):
            if isinstance(value.get("message"), str):
                issue_path = self._format_issue_path(value.get("path"))
                yield f"- {issue_path or path}: {value['message']}"
                return

            for key, item in value.items():
                yield from self._iter_error_detail_lines(item, f"{path}.{key}")
            return

        if value is not None:
            yield f"- {path}: {value}"

    def _format_issue_path(self, value: Any) -> str | None:
        if isinstance(value, str) and value:
            return value
        if not isinstance(value, list) or not value:
            return None

        path = ""
        for part in value:
            if isinstance(part, int):
                path = f"{path}[{part}]"
            else:
                key = str(part)
                path = f"{path}.{key}" if path else key
        return path or None
