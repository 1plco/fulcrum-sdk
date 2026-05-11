"""GitHub integration client for Fulcrum v1 APIs."""

from __future__ import annotations

from typing import Any

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class GithubResource(BaseResource):
    """Client for project GitHub v1 endpoints."""

    def get_repo(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "github/repo"))

    def link_repo(
        self,
        project_uuid: str,
        *,
        owner: str,
        repo_name: str,
        token_uuid: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "github/repo"),
            json=self._clean_params(
                owner=owner,
                repoName=repo_name,
                tokenUuid=token_uuid,
            ),
        )

    def disconnect_repo(self, project_uuid: str) -> JsonDict:
        return self._request("DELETE", self._project_path(project_uuid, "github/repo"))

    def create_repo(
        self,
        project_uuid: str,
        *,
        repo_name: str,
        org: str | None = None,
        is_private: bool | None = None,
        token_uuid: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "github/repo/create"),
            json=self._clean_params(
                repoName=repo_name,
                org=org,
                isPrivate=is_private,
                tokenUuid=token_uuid,
            ),
        )

    def list_repositories(
        self,
        project_uuid: str,
        *,
        token_uuid: str | None = None,
        org: str | None = None,
        source: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "github/repos"),
            params=self._clean_params(tokenUuid=token_uuid, org=org, source=source),
        )

    def list_organizations(
        self,
        project_uuid: str,
        *,
        token_uuid: str | None = None,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "github/orgs"),
            params=self._clean_params(tokenUuid=token_uuid),
        )

    def get_auth_url(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "github/auth-url"))

    def get_token(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "github/token"))

    def delete_token(
        self,
        project_uuid: str,
        *,
        token_uuid: str | None = None,
    ) -> JsonDict:
        return self._request(
            "DELETE",
            self._project_path(project_uuid, "github/token"),
            json=self._clean_params(tokenUuid=token_uuid),
        )

    def list_files(self, project_uuid: str, *, path: str | None = None) -> JsonDict:
        return self._request(
            "GET",
            self._project_path(project_uuid, "github/files"),
            params=self._clean_params(path=path),
        )

    def list_pull_requests(self, project_uuid: str) -> JsonDict:
        return self._request("GET", self._project_path(project_uuid, "github/prs"))

    def sync(self, project_uuid: str) -> JsonDict:
        return self._request("POST", self._project_path(project_uuid, "github/sync"))

    def refresh_template(self, project_uuid: str, payload: JsonDict | None = None) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "github/template-refresh"),
            json=payload or {},
        )

    def push_manifest(self, project_uuid: str, manifest: Any) -> JsonDict:
        return self._request(
            "POST",
            self._project_path(project_uuid, "github/push-manifest"),
            json={"manifest": manifest},
        )
