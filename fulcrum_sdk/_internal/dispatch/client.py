"""Best-effort dispatch client for Fulcrum runtime."""

import json
import os
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel

from fulcrum_sdk._internal.dispatch.models import (
    PAYLOAD_MAX_SIZE_BYTES,
    SCHEMA_VERSION,
    SUMMARY_MAX_LENGTH,
    DispatchEntry,
)
from fulcrum_sdk._internal.dispatch.redaction import redact_payload

DEFAULT_TIMEOUT_MS = 1500
DEFAULT_MAX_BYTES = PAYLOAD_MAX_SIZE_BYTES


class DispatchClient:
    """Best-effort dispatch client for Fulcrum runtime.

    This client sends dispatch entries to the Fulcrum API. It is designed to be
    best-effort: all methods return False on any error and never raise exceptions.

    Use `DispatchClient.from_env()` to create a client from environment variables.
    If required environment variables are missing, a no-op client is returned.
    """

    def __init__(
        self,
        *,
        dispatch_url: str | None = None,
        dispatch_token: str | None = None,
        ticket_uuid: str | None = None,
        run_uuid: str | None = None,
        message_uuid: str | None = None,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        max_bytes: int = DEFAULT_MAX_BYTES,
        debug: bool = False,
    ) -> None:
        """Initialize the dispatch client.

        Args:
            dispatch_url: The URL of the dispatch API endpoint.
            dispatch_token: The authentication token for the API.
            ticket_uuid: The UUID of the ticket to dispatch to.
            run_uuid: The UUID of the current run.
            message_uuid: Optional UUID of the current message.
            timeout_ms: Request timeout in milliseconds.
            max_bytes: Maximum payload size in bytes.
            debug: Enable debug logging to stderr.
        """
        self._dispatch_url = dispatch_url
        self._dispatch_token = dispatch_token
        self._ticket_uuid = ticket_uuid
        self._run_uuid = run_uuid
        self._message_uuid = message_uuid
        self._timeout_ms = timeout_ms
        self._max_bytes = max_bytes
        self._debug = debug
        self._enabled = all([dispatch_url, dispatch_token, ticket_uuid, run_uuid])

    @classmethod
    def from_env(cls) -> "DispatchClient":
        """Create a dispatch client from environment variables.

        Required environment variables:
            FULCRUM_DISPATCH_URL: The dispatch API endpoint URL.
            FULCRUM_DISPATCH_TOKEN: The authentication token.
            FULCRUM_TICKET_UUID: The ticket UUID.
            FULCRUM_RUN_UUID: The run UUID.

        Optional environment variables:
            FULCRUM_MESSAGE_UUID: The message UUID.
            FULCRUM_DISPATCH_DEBUG: Set to "1" to enable debug logging.
            FULCRUM_DISPATCH_TIMEOUT_MS: Request timeout in milliseconds.
            FULCRUM_DISPATCH_MAX_BYTES: Maximum payload size in bytes.

        Returns:
            A configured DispatchClient. If required env vars are missing,
            returns a no-op client (all dispatch methods return False).
        """
        dispatch_url = os.environ.get("FULCRUM_DISPATCH_URL")
        dispatch_token = os.environ.get("FULCRUM_DISPATCH_TOKEN")
        ticket_uuid = os.environ.get("FULCRUM_TICKET_UUID")
        run_uuid = os.environ.get("FULCRUM_RUN_UUID")
        message_uuid = os.environ.get("FULCRUM_MESSAGE_UUID")

        debug = os.environ.get("FULCRUM_DISPATCH_DEBUG", "") == "1"
        timeout_ms = int(os.environ.get("FULCRUM_DISPATCH_TIMEOUT_MS", str(DEFAULT_TIMEOUT_MS)))
        max_bytes = int(os.environ.get("FULCRUM_DISPATCH_MAX_BYTES", str(DEFAULT_MAX_BYTES)))

        return cls(
            dispatch_url=dispatch_url,
            dispatch_token=dispatch_token,
            ticket_uuid=ticket_uuid,
            run_uuid=run_uuid,
            message_uuid=message_uuid,
            timeout_ms=timeout_ms,
            max_bytes=max_bytes,
            debug=debug,
        )

    @property
    def enabled(self) -> bool:
        """Check if the client is properly configured and enabled."""
        return self._enabled

    def _log_debug(self, message: str) -> None:
        """Log a debug message to stderr if debug mode is enabled."""
        if self._debug:
            import sys

            print(f"[fulcrum-sdk] {message}", file=sys.stderr)

    def dispatch(
        self,
        kind: str,
        summary: str,
        payload: dict[str, Any] | None = None,
        *,
        source: str = "sdk",
        client_ts: str | None = None,
        skip_redaction: bool = False,
    ) -> bool:
        """Send a dispatch entry to the Fulcrum API.

        This is the core dispatch method. All other dispatch_* methods call this.

        Args:
            kind: Classification of the dispatch (e.g., 'text', 'api_call', 'db').
            summary: Human-readable summary, <= 512 chars, single line.
            payload: Optional structured data (will be redacted unless skip_redaction=True).
            source: Origin of the dispatch (default: "sdk").
            client_ts: Client timestamp (ISO string). Defaults to current time.
            skip_redaction: If True, skip automatic redaction of sensitive keys.

        Returns:
            True if the dispatch was sent successfully, False otherwise.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, skipping dispatch")
            return False

        try:
            # Truncate summary if too long
            if len(summary) > SUMMARY_MAX_LENGTH:
                summary = summary[: SUMMARY_MAX_LENGTH - 3] + "..."

            # Redact and truncate payload
            processed_payload: dict[str, Any] | None = None
            if payload is not None:
                processed_payload = redact_payload(payload, skip_redaction=skip_redaction)
                processed_payload = self._truncate_payload(processed_payload)

            # Build the entry
            entry = DispatchEntry(
                ticket_uuid=self._ticket_uuid,  # type: ignore[arg-type]
                run_uuid=self._run_uuid,  # type: ignore[arg-type]
                kind=kind,
                summary=summary.replace("\n", " "),  # Ensure single line
                message_uuid=self._message_uuid,
                payload=processed_payload,
                source=source,
                schema_version=SCHEMA_VERSION,
                client_ts=client_ts or datetime.now(UTC).isoformat(),
            )

            # Send the request
            self._log_debug(f"Sending dispatch: {entry.kind} - {entry.summary[:50]}")
            return self._send(entry)

        except Exception as e:
            self._log_debug(f"Dispatch failed: {e}")
            return False

    def _truncate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Truncate payload if it exceeds max bytes."""
        payload_json = json.dumps(payload, default=str)
        if len(payload_json.encode("utf-8")) <= self._max_bytes:
            return payload

        # Payload too large - return a truncation notice
        return {
            "_truncated": True,
            "_original_size": len(payload_json.encode("utf-8")),
            "_max_size": self._max_bytes,
        }

    def _send(self, entry: DispatchEntry) -> bool:
        """Send the dispatch entry to the API."""
        try:
            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.post(
                    self._dispatch_url,  # type: ignore[arg-type]
                    json=entry.model_dump(mode="json", exclude_none=True),
                    headers={
                        "Authorization": f"Bearer {self._dispatch_token}",
                        "Content-Type": "application/json",
                    },
                )
                if response.status_code >= 200 and response.status_code < 300:
                    self._log_debug("Dispatch succeeded")
                    return True
                else:
                    self._log_debug(f"Dispatch failed with status {response.status_code}")
                    return False
        except httpx.TimeoutException:
            self._log_debug("Dispatch timed out")
            return False
        except Exception as e:
            self._log_debug(f"Dispatch error: {e}")
            return False

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def dispatch_text(self, summary: str, text: str | None = None) -> bool:
        """Dispatch a text milestone.

        Args:
            summary: Human-readable summary of the text event.
            text: Optional additional text content.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        payload = {"text": text} if text is not None else None
        return self.dispatch("text", summary, payload)

    def dispatch_json(self, summary: str, payload: dict[str, Any]) -> bool:
        """Dispatch a JSON data event.

        Args:
            summary: Human-readable summary of the JSON operation.
            payload: The JSON data to dispatch.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        return self.dispatch("json", summary, payload)

    def dispatch_api_call(
        self,
        summary: str,
        service: str,
        operation: str,
        **details: Any,
    ) -> bool:
        """Dispatch an API call event.

        Args:
            summary: Human-readable summary of the API call.
            service: Service/provider name (e.g., "phonic", "claude", "mapbox").
            operation: Operation performed (e.g., "outbound_call", "generate_text").
            **details: Additional operation-specific fields.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        payload = {"service": service, "operation": operation, **details}
        return self.dispatch("api_call", summary, payload)

    def dispatch_external_ref(
        self,
        summary: str,
        provider: str,
        ref_type: str,
        ref_id: str,
        url: str | None = None,
    ) -> bool:
        """Dispatch an external reference event.

        Args:
            summary: Human-readable summary of the external reference.
            provider: Provider name (e.g., "browser-use", "pdf-skill").
            ref_type: Type of reference (e.g., "task", "document").
            ref_id: External reference ID.
            url: Optional URL to the external resource.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        payload: dict[str, Any] = {
            "provider": provider,
            "ref_type": ref_type,
            "ref_id": ref_id,
        }
        if url is not None:
            payload["url"] = url
        return self.dispatch("external_ref", summary, payload)

    def dispatch_db(
        self,
        summary: str,
        operation: str,
        table: str,
        rows: int | None = None,
        query: str | None = None,
    ) -> bool:
        """Dispatch a database operation event.

        Args:
            summary: Human-readable summary of the DB operation.
            operation: Operation type ('insert', 'update', 'delete', 'select').
            table: Table name.
            rows: Number of rows affected/returned.
            query: Optional query string (will be redacted of sensitive values).

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        payload: dict[str, Any] = {"operation": operation, "table": table}
        if rows is not None:
            payload["count"] = rows
        if query is not None:
            payload["query"] = query
        return self.dispatch("db", summary, payload)

    def dispatch_model(
        self,
        summary: str,
        model: BaseModel,
        input_summary: str | None = None,
    ) -> bool:
        """Dispatch a Pydantic model display event.

        Args:
            summary: Human-readable summary of what this model represents.
            model: The Pydantic model instance to display.
            input_summary: Optional brief description of the input source.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        payload: dict[str, Any] = {
            "model_name": model.__class__.__name__,
            "data": model.model_dump(mode="json"),
        }
        if input_summary is not None:
            payload["input_summary"] = input_summary
        return self.dispatch("model", summary, payload)


def get_dispatch_client() -> DispatchClient:
    """Get a dispatch client configured from environment variables.

    This is a convenience function that returns a DispatchClient configured
    from environment variables. If required variables are not set, returns
    a no-op client (all dispatch methods return False).

    Returns:
        A configured DispatchClient instance.
    """
    return DispatchClient.from_env()
