"""Best-effort improvements client for Fulcrum runtime."""

import json
import os
from typing import Any

import httpx

from fulcrum_sdk._internal.dispatch.redaction import redact_payload
from fulcrum_sdk._internal.improvements.models import (
    PAYLOAD_MAX_SIZE_BYTES,
    Improvement,
    ImprovementCreate,
    ImprovementEvent,
    ImprovementStatus,
    ImprovementUpdate,
)

DEFAULT_TIMEOUT_MS = 1500
DEFAULT_MAX_BYTES = PAYLOAD_MAX_SIZE_BYTES


class ImprovementsClient:
    """Best-effort improvements client for Fulcrum runtime.

    This client manages improvements (issues/suggestions) through the Fulcrum API.
    It is designed to be best-effort: all methods return False on any error and
    never raise exceptions.

    Use `ImprovementsClient.from_env()` to create a client from environment variables.
    If required environment variables are missing, a no-op client is returned.
    """

    def __init__(
        self,
        *,
        improvements_url: str | None = None,
        run_token: str | None = None,
        project_uuid: str | None = None,
        ticket_uuid: str | None = None,
        run_uuid: str | None = None,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        max_bytes: int = DEFAULT_MAX_BYTES,
        debug: bool = False,
    ) -> None:
        """Initialize the improvements client.

        Args:
            improvements_url: The URL of the improvements API endpoint.
            run_token: The authentication token for the API.
            project_uuid: The UUID of the project.
            ticket_uuid: The UUID of the ticket (optional).
            run_uuid: The UUID of the current run (required for auth).
            timeout_ms: Request timeout in milliseconds.
            max_bytes: Maximum payload size in bytes.
            debug: Enable debug logging to stderr.
        """
        self._improvements_url = improvements_url
        self._run_token = run_token
        self._project_uuid = project_uuid
        self._ticket_uuid = ticket_uuid
        self._run_uuid = run_uuid
        self._timeout_ms = timeout_ms
        self._max_bytes = max_bytes
        self._debug = debug
        self._enabled = all([improvements_url, run_token, run_uuid])

    @classmethod
    def from_env(cls) -> "ImprovementsClient":
        """Create an improvements client from environment variables.

        Required environment variables:
            FULCRUM_IMPROVEMENTS_URL: The improvements API endpoint URL.
            FULCRUM_RUN_TOKEN: The authentication token (preferred).
            FULCRUM_DISPATCH_TOKEN: Deprecated fallback for auth token.
            FULCRUM_RUN_UUID: The run UUID.

        Optional environment variables:
            FULCRUM_PROJECT_UUID: The project UUID.
            FULCRUM_TICKET_UUID: The ticket UUID.
            FULCRUM_IMPROVEMENTS_DEBUG: Set to "1" to enable debug logging.
            FULCRUM_IMPROVEMENTS_TIMEOUT_MS: Request timeout in milliseconds.
            FULCRUM_IMPROVEMENTS_MAX_BYTES: Maximum payload size in bytes.

        Returns:
            A configured ImprovementsClient. If required env vars are missing,
            returns a no-op client (all methods return False/empty list).
        """
        improvements_url = os.environ.get("FULCRUM_IMPROVEMENTS_URL")

        # Prefer FULCRUM_RUN_TOKEN, fallback to deprecated FULCRUM_DISPATCH_TOKEN
        run_token = os.environ.get("FULCRUM_RUN_TOKEN") or os.environ.get(
            "FULCRUM_DISPATCH_TOKEN"
        )

        project_uuid = os.environ.get("FULCRUM_PROJECT_UUID")
        ticket_uuid = os.environ.get("FULCRUM_TICKET_UUID")
        run_uuid = os.environ.get("FULCRUM_RUN_UUID")

        debug = os.environ.get("FULCRUM_IMPROVEMENTS_DEBUG", "") == "1"
        timeout_ms = int(
            os.environ.get("FULCRUM_IMPROVEMENTS_TIMEOUT_MS", str(DEFAULT_TIMEOUT_MS))
        )
        max_bytes = int(
            os.environ.get("FULCRUM_IMPROVEMENTS_MAX_BYTES", str(DEFAULT_MAX_BYTES))
        )

        return cls(
            improvements_url=improvements_url,
            run_token=run_token,
            project_uuid=project_uuid,
            ticket_uuid=ticket_uuid,
            run_uuid=run_uuid,
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

            print(f"[fulcrum-sdk:improvements] {message}", file=sys.stderr)

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Bearer {self._run_token}",
            "Content-Type": "application/json",
        }

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

    def list_improvements(
        self, project_uuid: str | None = None
    ) -> list[Improvement]:
        """List improvements for the current run or project.

        Args:
            project_uuid: Optional project UUID to filter by. If not provided,
                         uses the project_uuid from env vars.

        Returns:
            List of Improvement objects. Returns empty list on any error.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, returning empty list")
            return []

        try:
            params: dict[str, str] = {"run_uuid": self._run_uuid}  # type: ignore[dict-item]
            if project_uuid or self._project_uuid:
                params["project_uuid"] = project_uuid or self._project_uuid  # type: ignore[assignment]

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.get(
                    self._improvements_url,  # type: ignore[arg-type]
                    params=params,
                    headers=self._get_headers(),
                )
                if response.status_code >= 200 and response.status_code < 300:
                    data = response.json()
                    if isinstance(data, list):
                        improvements_data = data
                    elif isinstance(data, dict):
                        improvements_data = data.get("improvements", data)
                    else:
                        self._log_debug(f"Unexpected response format: {type(data)}")
                        return []

                    if isinstance(improvements_data, list):
                        return [Improvement(**item) for item in improvements_data]
                    self._log_debug(f"Unexpected response format: {type(improvements_data)}")
                    return []
                else:
                    self._log_debug(f"List failed with status {response.status_code}")
                    return []
        except httpx.TimeoutException:
            self._log_debug("List request timed out")
            return []
        except Exception as e:
            self._log_debug(f"List error: {e}")
            return []

    def create_improvement(
        self,
        title: str,
        description: str | None = None,
        dedupe_key: str | None = None,
        status: ImprovementStatus = "open",
    ) -> bool:
        """Create a new improvement.

        Args:
            title: Brief title for the improvement.
            description: Detailed description of the improvement.
            dedupe_key: Key for deduplication (prevents duplicates).
            status: Initial status (default: 'open').

        Returns:
            True if the improvement was created successfully, False otherwise.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, skipping create")
            return False

        try:
            payload = ImprovementCreate(
                title=title,
                description=description,
                dedupe_key=dedupe_key,
                status=status,
            )

            request_body: dict[str, Any] = {
                "run_uuid": self._run_uuid,
                **payload.model_dump(mode="json", exclude_none=True),
            }
            if self._project_uuid:
                request_body["project_uuid"] = self._project_uuid
            if self._ticket_uuid:
                request_body["ticket_uuid"] = self._ticket_uuid

            self._log_debug(f"Creating improvement: {title[:50]}")

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.post(
                    self._improvements_url,  # type: ignore[arg-type]
                    json=request_body,
                    headers=self._get_headers(),
                )
                if response.status_code >= 200 and response.status_code < 300:
                    self._log_debug("Create succeeded")
                    return True
                else:
                    self._log_debug(f"Create failed with status {response.status_code}")
                    return False
        except httpx.TimeoutException:
            self._log_debug("Create request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Create error: {e}")
            return False

    def update_improvement(
        self,
        uuid: str,
        **fields: Any,
    ) -> bool:
        """Update an existing improvement.

        Args:
            uuid: The UUID of the improvement to update.
            **fields: Fields to update (title, description, status).

        Returns:
            True if the improvement was updated successfully, False otherwise.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, skipping update")
            return False

        try:
            # Filter to valid fields
            valid_fields = {
                k: v
                for k, v in fields.items()
                if k in ("title", "description", "status") and v is not None
            }

            if not valid_fields:
                self._log_debug("No valid fields to update")
                return False

            payload = ImprovementUpdate(**valid_fields)
            request_body: dict[str, Any] = {
                "run_uuid": self._run_uuid,
                **payload.model_dump(mode="json", exclude_none=True),
            }

            url = f"{self._improvements_url}/{uuid}"
            self._log_debug(f"Updating improvement: {uuid}")

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.patch(
                    url,
                    json=request_body,
                    headers=self._get_headers(),
                )
                if response.status_code >= 200 and response.status_code < 300:
                    self._log_debug("Update succeeded")
                    return True
                else:
                    self._log_debug(f"Update failed with status {response.status_code}")
                    return False
        except httpx.TimeoutException:
            self._log_debug("Update request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Update error: {e}")
            return False

    def delete_improvement(self, uuid: str) -> bool:
        """Delete an improvement.

        Args:
            uuid: The UUID of the improvement to delete.

        Returns:
            True if the improvement was deleted successfully, False otherwise.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, skipping delete")
            return False

        try:
            url = f"{self._improvements_url}/{uuid}"
            params = {"run_uuid": self._run_uuid}

            self._log_debug(f"Deleting improvement: {uuid}")

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.delete(
                    url,
                    params=params,
                    headers=self._get_headers(),
                )
                if response.status_code >= 200 and response.status_code < 300:
                    self._log_debug("Delete succeeded")
                    return True
                else:
                    self._log_debug(f"Delete failed with status {response.status_code}")
                    return False
        except httpx.TimeoutException:
            self._log_debug("Delete request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Delete error: {e}")
            return False

    def emit_improvement_event(
        self,
        improvement_uuid: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        """Emit an event for an improvement.

        Args:
            improvement_uuid: The UUID of the improvement.
            action: The action being recorded.
            payload: Optional additional data for the event.

        Returns:
            True if the event was emitted successfully, False otherwise.
        """
        if not self._enabled:
            self._log_debug("Client not enabled, skipping event")
            return False

        try:
            # Redact and truncate payload if provided
            processed_payload: dict[str, Any] | None = None
            if payload is not None:
                processed_payload = redact_payload(payload)
                processed_payload = self._truncate_payload(processed_payload)

            event = ImprovementEvent(
                improvement_uuid=improvement_uuid,
                action=action,
                payload=processed_payload,
            )

            request_body: dict[str, Any] = {
                "run_uuid": self._run_uuid,
                **event.model_dump(mode="json", exclude_none=True),
            }

            url = f"{self._improvements_url}/{improvement_uuid}/events"
            self._log_debug(f"Emitting event: {action} for {improvement_uuid}")

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.post(
                    url,
                    json=request_body,
                    headers=self._get_headers(),
                )
                if response.status_code >= 200 and response.status_code < 300:
                    self._log_debug("Event emitted successfully")
                    return True
                else:
                    self._log_debug(f"Event failed with status {response.status_code}")
                    return False
        except httpx.TimeoutException:
            self._log_debug("Event request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Event error: {e}")
            return False


def get_improvements_client() -> ImprovementsClient:
    """Get an improvements client configured from environment variables.

    This is a convenience function that returns an ImprovementsClient configured
    from environment variables. If required variables are not set, returns
    a no-op client (all methods return False/empty list).

    Returns:
        A configured ImprovementsClient instance.
    """
    return ImprovementsClient.from_env()
