"""SOP sync client for Fulcrum v1 APIs."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class SopSyncResource(BaseResource):
    """Client for SOP sync v1 endpoints."""

    def status(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "sop-sync/status"))

    def pull(self, project_uuid: str) -> JsonDict:
        return self._request("POST", self._project_path(project_uuid, "sop-sync/pull"))

    def push(self, project_uuid: str) -> JsonDict:
        return self._request("POST", self._project_path(project_uuid, "sop-sync/push"))
