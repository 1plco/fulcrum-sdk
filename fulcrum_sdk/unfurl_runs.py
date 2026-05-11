"""Project unfurl run client for Fulcrum v1 APIs."""

from __future__ import annotations

import httpx

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class UnfurlRunsResource(BaseResource):
    """Client for project unfurl run v1 endpoints."""

    def list(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "unfurl-runs"),
            params=self._pagination_params(cursor=cursor, limit=limit, status=status),
        )

    def start(
        self,
        project_uuid: str,
        sop_uuid: str,
        *,
        stream: bool = False,
        cancel_on_disconnect: bool = False,
    ) -> JsonDict | httpx.Response:
        if stream:
            headers = {"Accept": "text/event-stream"}
            if cancel_on_disconnect:
                headers["X-Cancel-On-Disconnect"] = "1"
            return self._stream_request(
                "POST",
                self._project_path(project_uuid, "unfurl-runs"),
                json={"sopUuid": sop_uuid},
                headers=headers,
            )

        return self._request(
            "POST",
            self._project_path(project_uuid, "unfurl-runs"),
            json={"sopUuid": sop_uuid},
        )

    def get(self, project_uuid: str, run_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "unfurl-runs", run_uuid),
        )

    def list_events(
        self,
        project_uuid: str,
        run_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "unfurl-runs", run_uuid, "events"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def list_files(
        self,
        project_uuid: str,
        run_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "unfurl-runs", run_uuid, "files"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def get_file_signed_url(
        self,
        project_uuid: str,
        run_uuid: str,
        file_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "unfurl-runs",
                run_uuid,
                "files",
                file_uuid,
                "signed-url",
            ),
        )

    def interrupt(
        self,
        project_uuid: str,
        *,
        run_uuid: str | None = None,
        sandbox_id: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "unfurl-runs/interrupt"),
            json=self._clean_params(runUuid=run_uuid, sandboxId=sandbox_id),
        )
