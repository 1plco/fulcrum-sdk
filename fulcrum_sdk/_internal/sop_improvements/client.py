"""Best-effort semantic SOP improvements client for Fulcrum runtime."""

import os
from typing import Any

import httpx

from fulcrum_sdk._internal.sop_improvements.models import (
    SopImprovement,
    SopImprovementCreate,
)

DEFAULT_TIMEOUT_MS = 1500


class SopImprovementsClient:
    """Client for semantic SOP improvement suggestions."""

    def __init__(
        self,
        *,
        sop_improvements_url: str | None = None,
        run_token: str | None = None,
        project_uuid: str | None = None,
        ticket_uuid: str | None = None,
        run_uuid: str | None = None,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        debug: bool = False,
    ) -> None:
        self._sop_improvements_url = sop_improvements_url
        self._run_token = run_token
        self._project_uuid = project_uuid
        self._ticket_uuid = ticket_uuid
        self._run_uuid = run_uuid
        self._timeout_ms = timeout_ms
        self._debug = debug
        self._enabled = all([sop_improvements_url, run_token, run_uuid])

    @classmethod
    def from_env(cls) -> "SopImprovementsClient":
        """Create a SOP improvements client from environment variables."""

        run_token = os.environ.get("FULCRUM_RUN_TOKEN") or os.environ.get("FULCRUM_DISPATCH_TOKEN")

        return cls(
            sop_improvements_url=os.environ.get("FULCRUM_SOP_IMPROVEMENTS_URL"),
            run_token=run_token,
            project_uuid=os.environ.get("FULCRUM_PROJECT_UUID"),
            ticket_uuid=os.environ.get("FULCRUM_TICKET_UUID"),
            run_uuid=os.environ.get("FULCRUM_RUN_UUID"),
            timeout_ms=int(
                os.environ.get("FULCRUM_SOP_IMPROVEMENTS_TIMEOUT_MS", str(DEFAULT_TIMEOUT_MS))
            ),
            debug=os.environ.get("FULCRUM_SOP_IMPROVEMENTS_DEBUG", "") == "1",
        )

    @property
    def enabled(self) -> bool:
        """Return True when required runtime configuration is present."""

        return self._enabled

    def _log_debug(self, message: str) -> None:
        if self._debug:
            import sys

            print(f"[fulcrum-sdk:sop-improvements] {message}", file=sys.stderr)

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._run_token}",
            "Content-Type": "application/json",
        }

    def list_sop_improvements(
        self,
        project_uuid: str | None = None,
        *,
        status: str | None = None,
    ) -> list[SopImprovement]:
        """List semantic SOP improvements for the current project/run."""

        if not self._enabled:
            self._log_debug("Client not enabled, returning empty list")
            return []

        try:
            params: dict[str, str] = {"run_uuid": self._run_uuid}  # type: ignore[dict-item]
            if project_uuid or self._project_uuid:
                params["project_uuid"] = project_uuid or self._project_uuid  # type: ignore[assignment]
            if status:
                params["status"] = status

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.get(
                    self._sop_improvements_url,  # type: ignore[arg-type]
                    params=params,
                    headers=self._get_headers(),
                )
                if 200 <= response.status_code < 300:
                    data = response.json()
                    if isinstance(data, list):
                        improvements_data = data
                    elif isinstance(data, dict):
                        improvements_data = data.get(
                            "sop_improvements", data.get("improvements", [])
                        )
                    else:
                        return []

                    if isinstance(improvements_data, list):
                        return [SopImprovement(**item) for item in improvements_data]
                self._log_debug(f"List failed with status {response.status_code}")
                return []
        except httpx.TimeoutException:
            self._log_debug("List request timed out")
            return []
        except Exception as e:
            self._log_debug(f"List error: {e}")
            return []

    def create_sop_improvement(
        self,
        title: str,
        *,
        description: str | None = None,
        observed_gap: str | None = None,
        suggested_change: str | None = None,
        section_anchor: str | None = None,
        severity: str = "normal",
        dedupe_key: str | None = None,
        source_guidance_request_uuid: str | None = None,
    ) -> bool:
        """Create a semantic SOP improvement suggestion."""

        if not self._enabled:
            self._log_debug("Client not enabled, skipping create")
            return False

        try:
            payload = SopImprovementCreate(
                title=title,
                description=description,
                observed_gap=observed_gap,
                suggested_change=suggested_change,
                section_anchor=section_anchor,
                severity=severity,
                dedupe_key=dedupe_key,
                source_guidance_request_uuid=source_guidance_request_uuid,
            )

            request_body: dict[str, Any] = {
                "run_uuid": self._run_uuid,
                **payload.model_dump(mode="json", exclude_none=True),
            }
            if self._project_uuid:
                request_body["project_uuid"] = self._project_uuid
            if self._ticket_uuid:
                request_body["ticket_uuid"] = self._ticket_uuid

            with httpx.Client(timeout=self._timeout_ms / 1000) as client:
                response = client.post(
                    self._sop_improvements_url,  # type: ignore[arg-type]
                    json=request_body,
                    headers=self._get_headers(),
                )
                if 200 <= response.status_code < 300:
                    self._log_debug("Create succeeded")
                    return True

                self._log_debug(f"Create failed with status {response.status_code}")
                return False
        except httpx.TimeoutException:
            self._log_debug("Create request timed out")
            return False
        except Exception as e:
            self._log_debug(f"Create error: {e}")
            return False


def get_sop_improvements_client() -> SopImprovementsClient:
    """Get a semantic SOP improvements client configured from environment."""

    return SopImprovementsClient.from_env()
