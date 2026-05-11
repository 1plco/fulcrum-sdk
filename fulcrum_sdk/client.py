"""User-facing Fulcrum client."""

from __future__ import annotations

import os

from fulcrum_sdk._internal.http import DEFAULT_TIMEOUT
from fulcrum_sdk.exceptions import FulcrumConfigError
from fulcrum_sdk.tickets import TicketsResource


class FulcrumClient:
    """Client for Fulcrum public v1 APIs."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        resolved_base_url = base_url or os.environ.get("FULCRUM_BASE_URL")
        if not resolved_base_url:
            raise FulcrumConfigError("base_url or FULCRUM_BASE_URL is required")

        self._api_key = (
            api_key
            or os.environ.get("FULCRUM_API_KEY")
            or os.environ.get("FULCRUM_RUN_TOKEN")
        )
        self._base_url = resolved_base_url
        self._timeout = timeout
        self._tickets: TicketsResource | None = None

    @property
    def tickets(self) -> TicketsResource:
        if self._tickets is None:
            self._tickets = TicketsResource(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._tickets
