"""User-facing Fulcrum client."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import httpx

from fulcrum_sdk._internal.http import DEFAULT_TIMEOUT, create_http_client
from fulcrum_sdk.exceptions import FulcrumAPIError, FulcrumConfigError
from fulcrum_sdk.models import JsonDict
from fulcrum_sdk.tickets import TicketsResource

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
            or os.environ.get("FULCRUM_RUNTIME_TOKEN")
            or os.environ.get("FULCRUM_API_KEY")
            or os.environ.get("FULCRUM_RUN_TOKEN")
        )
        self._base_url = resolved_base_url.rstrip("/")
        self._max_retries = max(0, max_retries)
        self._retry_delay_seconds = max(0.0, retry_delay_seconds)
        self._timeout = timeout
        self._tickets: TicketsResource | None = None

    @classmethod
    def from_env(cls) -> FulcrumClient:
        """Create a client from FULCRUM_API_BASE_URL and FULCRUM_RUNTIME_TOKEN."""
        return cls()

    @property
    def tickets(self) -> TicketsResource:
        if self._tickets is None:
            self._tickets = TicketsResource(client=self)
        return self._tickets

    def request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> JsonDict | httpx.Response:
        """Call a Fulcrum v1 API path.

        Args:
            method: HTTP method.
            path: Absolute API path such as /api/v1/projects.
            json: Optional JSON request body.
            params: Optional query parameters.
            stream: When true, return the raw response for caller-managed streaming.

        Returns:
            Unwrapped response data for JSON routes, or a raw response for streams.
        """
        if stream:
            return self._stream_request(method, path, json=json, params=params)

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                with self._client() as client:
                    response = client.request(
                        method,
                        path,
                        headers=self._headers(),
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

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _stream_request(
        self,
        method: str,
        path: str,
        *,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        client = create_http_client(timeout=self._timeout, base_url=self._base_url)
        response = client.build_request(
            method,
            path,
            headers=self._headers(),
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
        try:
            body = httpx.Response(status_code, content=body_text).json()
        except ValueError:
            body = None

        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                message = error["message"]
            elif isinstance(body.get("message"), str):
                message = body["message"]

        return FulcrumAPIError(message, status_code, snippet)
