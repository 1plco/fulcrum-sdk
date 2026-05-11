"""Project improvement client for Fulcrum v1 APIs."""

from __future__ import annotations

from collections.abc import Sequence

import httpx

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class ImprovementsResource(BaseResource):
    """Client for project improvements and improvement runs."""

    def list(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
        include_deleted: bool | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvements"),
            params=self._pagination_params(
                cursor=cursor,
                limit=limit,
                status=status,
                includeDeleted=("true" if include_deleted else None),
            ),
        )

    def create(
        self,
        project_uuid: str,
        *,
        title: str,
        description: str | None = None,
        status: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "improvements"),
            json=self._clean_params(
                title=title,
                description=description,
                status=status,
            ),
        )

    def get(self, project_uuid: str, improvement_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvements", improvement_uuid),
        )

    def update(
        self,
        project_uuid: str,
        improvement_uuid: str,
        *,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._project_path(project_uuid, "improvements", improvement_uuid),
            json=self._clean_params(
                title=title,
                description=description,
                status=status,
            ),
        )

    def delete(self, project_uuid: str, improvement_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "improvements", improvement_uuid),
        )

    def restore(self, project_uuid: str, improvement_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "improvements", improvement_uuid, "restore"),
        )

    def list_events(
        self,
        project_uuid: str,
        improvement_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvements", improvement_uuid, "events"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def list_runs(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvement-runs"),
            params=self._pagination_params(cursor=cursor, limit=limit, status=status),
        )

    def start_run(
        self,
        project_uuid: str,
        improvement_uuids: Sequence[str],
        *,
        stream: bool = False,
        cancel_on_disconnect: bool = False,
    ) -> JsonDict | httpx.Response:
        headers = None
        if stream:
            headers = {"Accept": "text/event-stream"}
            if cancel_on_disconnect:
                headers["X-Cancel-On-Disconnect"] = "1"
            return self._stream_request(
                "POST",
                self._project_path(project_uuid, "improvement-runs"),
                json={"improvementUuids": improvement_uuids},
                headers=headers,
            )

        return self._request(
            "POST",
            self._project_path(project_uuid, "improvement-runs"),
            json={"improvementUuids": improvement_uuids},
        )

    def get_run(self, project_uuid: str, run_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvement-runs", run_uuid),
        )

    def list_run_events(
        self,
        project_uuid: str,
        run_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvement-runs", run_uuid, "events"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def list_run_files(
        self,
        project_uuid: str,
        run_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "improvement-runs", run_uuid, "files"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def get_run_file_signed_url(
        self,
        project_uuid: str,
        run_uuid: str,
        file_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "improvement-runs",
                run_uuid,
                "files",
                file_uuid,
                "signed-url",
            ),
        )

    def interrupt_run(
        self,
        project_uuid: str,
        *,
        run_uuid: str | None = None,
        sandbox_id: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "improvement-runs/interrupt"),
            json=self._clean_params(runUuid=run_uuid, sandboxId=sandbox_id),
        )
