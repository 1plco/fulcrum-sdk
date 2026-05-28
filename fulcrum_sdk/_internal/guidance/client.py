"""Guidance client for blocking SOP edge cases."""

import json
import os
from typing import Any

import httpx

from fulcrum_sdk._internal.dispatch.redaction import redact_payload
from fulcrum_sdk._internal.guidance.models import (
    CONTEXT_MAX_SIZE_BYTES,
    GuidanceRequestResult,
    GuidanceSeek,
)

DEFAULT_TIMEOUT_MS = 5000
DEFAULT_MAX_BYTES = CONTEXT_MAX_SIZE_BYTES


class GuidanceRequested(RuntimeError):
    """Raised after Fulcrum accepts a guidance request.

    Agents should let this exception stop the current script/step, then wait for
    the platform to resume execution with the user's guidance.
    """

    def __init__(self, result: GuidanceRequestResult) -> None:
        self.result = result
        super().__init__(f"Fulcrum guidance requested: {result.request_uuid} ({result.status})")


class GuidanceClient:
    """Client for requesting user guidance during project-ticket execution."""

    def __init__(
        self,
        *,
        guidance_url: str | None = None,
        run_token: str | None = None,
        project_uuid: str | None = None,
        ticket_uuid: str | None = None,
        run_uuid: str | None = None,
        message_uuid: str | None = None,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        max_bytes: int = DEFAULT_MAX_BYTES,
        debug: bool = False,
    ) -> None:
        self._guidance_url = guidance_url
        self._run_token = run_token
        self._project_uuid = project_uuid
        self._ticket_uuid = ticket_uuid
        self._run_uuid = run_uuid
        self._message_uuid = message_uuid
        self._timeout_ms = timeout_ms
        self._max_bytes = max_bytes
        self._debug = debug
        self._enabled = all([guidance_url, run_token, ticket_uuid, run_uuid])

    @classmethod
    def from_env(cls) -> "GuidanceClient":
        """Create a guidance client from Fulcrum runtime environment variables."""

        run_token = os.environ.get("FULCRUM_RUN_TOKEN") or os.environ.get("FULCRUM_DISPATCH_TOKEN")

        return cls(
            guidance_url=os.environ.get("FULCRUM_GUIDANCE_URL"),
            run_token=run_token,
            project_uuid=os.environ.get("FULCRUM_PROJECT_UUID"),
            ticket_uuid=os.environ.get("FULCRUM_TICKET_UUID"),
            run_uuid=os.environ.get("FULCRUM_RUN_UUID"),
            message_uuid=os.environ.get("FULCRUM_MESSAGE_UUID"),
            timeout_ms=int(os.environ.get("FULCRUM_GUIDANCE_TIMEOUT_MS", str(DEFAULT_TIMEOUT_MS))),
            max_bytes=int(os.environ.get("FULCRUM_GUIDANCE_MAX_BYTES", str(DEFAULT_MAX_BYTES))),
            debug=os.environ.get("FULCRUM_GUIDANCE_DEBUG", "") == "1",
        )

    @property
    def enabled(self) -> bool:
        """Return True when required runtime configuration is present."""

        return self._enabled

    def _log_debug(self, message: str) -> None:
        if self._debug:
            import sys

            print(f"[fulcrum-sdk:guidance] {message}", file=sys.stderr)

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._run_token}",
            "Content-Type": "application/json",
        }

    def _truncate_context(self, context: dict[str, Any]) -> dict[str, Any]:
        context_json = json.dumps(context, default=str)
        if len(context_json.encode("utf-8")) <= self._max_bytes:
            return context

        return {
            "_truncated": True,
            "_original_size": len(context_json.encode("utf-8")),
            "_max_size": self._max_bytes,
        }

    @staticmethod
    def _parse_result(data: Any) -> GuidanceRequestResult:
        if not isinstance(data, dict):
            return GuidanceRequestResult(request_uuid="unknown", status="pending")

        request = data.get("guidance_request")
        if not isinstance(request, dict):
            request = data.get("request") if isinstance(data.get("request"), dict) else None

        request_uuid = (
            data.get("request_uuid")
            or data.get("requestUuid")
            or (request or {}).get("uuid")
            or (request or {}).get("request_uuid")
            or "unknown"
        )
        status = data.get("status") or (request or {}).get("status") or "pending"

        return GuidanceRequestResult(
            request_uuid=str(request_uuid),
            status=str(status),
            guidance_request=request,
        )

    def seek_guidance(
        self,
        question: str,
        *,
        sop_section: str | None = None,
        severity: str = "severe",
        context: dict[str, Any] | None = None,
        raise_on_accept: bool = True,
    ) -> GuidanceRequestResult | bool:
        """Ask the user for guidance on a severe SOP edge case.

        Returns False when the client is disabled or the request fails. When
        Fulcrum accepts the request, the default behavior is to raise
        GuidanceRequested so execution stops instead of continuing with guessed
        SOP policy. Set raise_on_accept=False in tests or custom callers that
        need to inspect the accepted request.
        """

        if not self._enabled:
            self._log_debug("Client not enabled, skipping guidance request")
            return False

        try:
            payload = GuidanceSeek(
                question=question,
                severity=severity,
                sop_section=sop_section,
                context=context,
            )
            processed_context: dict[str, Any] | None = None
            if payload.context is not None:
                processed_context = self._truncate_context(redact_payload(payload.context))

            request_body: dict[str, Any] = {
                "run_uuid": self._run_uuid,
                "ticket_uuid": self._ticket_uuid,
                **payload.model_dump(mode="json", exclude_none=True, exclude={"context"}),
            }
            if processed_context is not None:
                request_body["context"] = processed_context
            if self._project_uuid:
                request_body["project_uuid"] = self._project_uuid
            if self._message_uuid:
                request_body["message_uuid"] = self._message_uuid

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.post(
                    self._guidance_url,  # type: ignore[arg-type]
                    json=request_body,
                    headers=self._get_headers(),
                )
                if 200 <= response.status_code < 300:
                    result = self._parse_result(response.json())
                    self._log_debug(f"Guidance request accepted: {result.request_uuid}")
                    if raise_on_accept:
                        raise GuidanceRequested(result)
                    return result

                self._log_debug(f"Guidance request failed with status {response.status_code}")
                return False
        except GuidanceRequested:
            raise
        except httpx.TimeoutException:
            self._log_debug("Guidance request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Guidance request error: {e}")
            return False


def get_guidance_client() -> GuidanceClient:
    """Get a guidance client configured from environment variables."""

    return GuidanceClient.from_env()
