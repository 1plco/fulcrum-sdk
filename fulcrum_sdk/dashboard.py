"""Dashboard client for Fulcrum v1 APIs."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class DashboardResource(BaseResource):
    """Client for project dashboard v1 endpoints."""

    def get(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "dashboard"))

    def costs(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "dashboard/costs"))
