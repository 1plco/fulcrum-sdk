"""Operator and computer client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class OperatorResource(BaseResource):
    """Client for operator/computer v1 endpoints."""

    def list_runtime_hosts(self, project_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/runtime-hosts"),
        )

    def get_runtime_host(self, project_uuid: str, runtime_host_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/runtime-hosts",
                runtime_host_uuid,
            ),
        )

    def get_current_runtime_host(self, project_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/runtime-hosts/current"),
        )

    def restart_runtime_host(self, project_uuid: str, runtime_host_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/runtime-hosts",
                runtime_host_uuid,
                "restart",
            ),
        )

    def stop_runtime_host(self, project_uuid: str, runtime_host_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/runtime-hosts",
                runtime_host_uuid,
                "stop",
            ),
        )

    def create_runtime_client_session(
        self,
        project_uuid: str,
        runtime_host_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/runtime-hosts",
                runtime_host_uuid,
                "client-sessions",
            ),
            json=payload or {},
        )

    def heartbeat_runtime_client_session(
        self,
        project_uuid: str,
        client_session_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/runtime-client-sessions",
                client_session_uuid,
                "heartbeat",
            ),
            json=payload or {},
        )

    def release_runtime_client_session(
        self,
        project_uuid: str,
        client_session_uuid: str,
    ) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(
                project_uuid,
                "operator/runtime-client-sessions",
                client_session_uuid,
            ),
        )

    def create_iframe_session(
        self,
        project_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "operator/iframe-sessions"),
            json=payload,
        )

    def get_iframe_session(self, project_uuid: str, session_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/iframe-sessions", session_uuid),
        )

    def delete_iframe_session(self, project_uuid: str, session_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "operator/iframe-sessions", session_uuid),
        )

    def create_widget_session(
        self,
        project_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "operator/widget-sessions"),
            json=payload,
        )

    def get_widget_session(
        self,
        project_uuid: str,
        widget_session_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/widget-sessions",
                widget_session_uuid,
            ),
        )

    def widget_session_events(
        self,
        project_uuid: str,
        widget_session_uuid: str,
        *,
        after_sequence: int | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/widget-sessions",
                widget_session_uuid,
                "events",
            ),
            params=self._clean_params(afterSequence=after_sequence, limit=limit),
        )

    def restart_widget_session(
        self,
        project_uuid: str,
        widget_session_uuid: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/widget-sessions",
                widget_session_uuid,
                "restart",
            ),
        )

    def disable_widget_session(
        self,
        project_uuid: str,
        widget_session_uuid: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/widget-sessions",
                widget_session_uuid,
                "disable",
            ),
        )

    def list_canvases(
        self,
        project_uuid: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/canvases"),
            params=self._pagination_params(cursor=cursor, limit=limit),
        )

    def create_canvas(self, project_uuid: str, payload: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "operator/canvases"),
            json=payload,
        )

    def get_canvas(self, project_uuid: str, canvas_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/canvases", canvas_uuid),
        )

    def update_canvas(
        self,
        project_uuid: str,
        canvas_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._project_path(project_uuid, "operator/canvases", canvas_uuid),
            json=payload,
        )

    def delete_canvas(self, project_uuid: str, canvas_uuid: str) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "operator/canvases", canvas_uuid),
        )

    def create_canvas_instance(
        self,
        project_uuid: str,
        canvas_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/canvases",
                canvas_uuid,
                "instances",
            ),
            json=payload,
        )

    def update_canvas_instance(
        self,
        project_uuid: str,
        canvas_uuid: str,
        instance_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._project_path(
                project_uuid,
                "operator/canvases",
                canvas_uuid,
                "instances",
                instance_uuid,
            ),
            json=payload,
        )

    def delete_canvas_instance(
        self,
        project_uuid: str,
        canvas_uuid: str,
        instance_uuid: str,
    ) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(
                project_uuid,
                "operator/canvases",
                canvas_uuid,
                "instances",
                instance_uuid,
            ),
        )

    def plan_canvas_builder(
        self,
        project_uuid: str,
        canvas_uuid: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/canvases",
                canvas_uuid,
                "builder/plan",
            ),
            json=payload,
        )

    def get_canvas_builder_run(
        self,
        project_uuid: str,
        builder_run_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/canvas-builder-runs",
                builder_run_uuid,
            ),
        )

    def apply_canvas_builder_run(
        self,
        project_uuid: str,
        builder_run_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/canvas-builder-runs",
                builder_run_uuid,
                "apply",
            ),
            json=payload or {},
        )

    def cancel_canvas_builder_run(
        self,
        project_uuid: str,
        builder_run_uuid: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/canvas-builder-runs",
                builder_run_uuid,
                "cancel",
            ),
        )

    def list_external_apis(self, project_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/external-apis"),
        )

    def test_external_api(
        self,
        project_uuid: str,
        provider_id: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/external-apis",
                provider_id,
                "test",
            ),
            json=payload or {},
        )

    def override_external_api(
        self,
        project_uuid: str,
        provider_id: str,
        payload: JsonDict,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/external-apis",
                provider_id,
                "override",
            ),
            json=payload,
        )

    def list_grants(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "operator/grants"))

    def request_current_grant(
        self,
        project_uuid: str,
        grant_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/grants",
                grant_uuid,
                "request-current",
            ),
            json=payload or {},
        )

    def revoke_grant(
        self,
        project_uuid: str,
        grant_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "operator/grants", grant_uuid, "revoke"),
            json=payload or {},
        )

    def approve_grant_request(
        self,
        project_uuid: str,
        grant_request_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/grant-requests",
                grant_request_uuid,
                "approve",
            ),
            json=payload or {},
        )

    def deny_grant_request(
        self,
        project_uuid: str,
        grant_request_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/grant-requests",
                grant_request_uuid,
                "deny",
            ),
            json=payload or {},
        )

    def confirm_action(
        self,
        project_uuid: str,
        confirmation_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/action-confirmations",
                confirmation_uuid,
                "confirm",
            ),
            json=payload or {},
        )

    def deny_action(
        self,
        project_uuid: str,
        confirmation_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/action-confirmations",
                confirmation_uuid,
                "deny",
            ),
            json=payload or {},
        )

    def get_build_run(self, project_uuid: str, build_run_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "operator/build-runs", build_run_uuid),
        )

    def list_build_run_events(
        self,
        project_uuid: str,
        build_run_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/build-runs",
                build_run_uuid,
                "events",
            ),
        )

    def interrupt_build_run(
        self,
        project_uuid: str,
        build_run_uuid: str,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/build-runs",
                build_run_uuid,
                "interrupt",
            ),
            json=payload or {},
        )

    def list_widget_versions(self, project_uuid: str, widget_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/widgets",
                widget_uuid,
                "versions",
            ),
        )

    def get_widget_version(
        self,
        project_uuid: str,
        widget_uuid: str,
        version_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/widgets",
                widget_uuid,
                "versions",
                version_uuid,
            ),
        )

    def activate_widget_version(
        self,
        project_uuid: str,
        widget_uuid: str,
        version_uuid: str,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(
                project_uuid,
                "operator/widgets",
                widget_uuid,
                "versions",
                version_uuid,
                "activate",
            ),
        )

    def list_widget_builds(self, project_uuid: str, widget_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(
                project_uuid,
                "operator/widgets",
                widget_uuid,
                "builds",
            ),
        )

    def team_path(self, team_uuid: str, *segments: str) -> str:
        """Build a future team-operator path for callers using low-level request."""
        return self._team_path(team_uuid, "operator", *segments)

    def request_team_operator(
        self,
        team_uuid: str,
        method: str,
        *segments: str,
        json: JsonDict | None = None,
        params: dict[str, Any] | None = None,
    ) -> JsonDict:
        return self._request(
            method,
            self.team_path(team_uuid, *segments),
            json=json,
            params=params,
        )
