"""Team ticket client for Fulcrum v1 APIs."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class TeamTicketsResource(BaseResource):
    """Client for team ticket v1 endpoints."""

    def list(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "tickets"))

    def create(
        self,
        team_uuid: str,
        *,
        prompt: str,
        title: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "tickets"),
            json=self._clean_params(prompt=prompt, title=title),
        )

    def get(self, team_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "tickets", ticket_uuid),
        )

    def update(
        self,
        team_uuid: str,
        ticket_uuid: str,
        *,
        title: str | None = None,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._team_path(team_uuid, "tickets", ticket_uuid),
            json={"title": title},
        )

    def list_messages(self, team_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "tickets", ticket_uuid, "messages"),
        )

    def add_message(
        self,
        team_uuid: str,
        ticket_uuid: str,
        *,
        content: str,
        role: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "tickets", ticket_uuid, "messages"),
            json=self._clean_params(content=content, role=role),
        )

    def execute(
        self,
        team_uuid: str,
        ticket_uuid: str,
        *,
        message_uuid: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "tickets", ticket_uuid, "execute"),
            json=self._clean_params(messageUuid=message_uuid),
        )

    def interrupt(self, team_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "tickets", ticket_uuid, "interrupt"),
        )

    def list_runs(self, team_uuid: str, ticket_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "tickets", ticket_uuid, "runs"),
        )

    def get_run(self, team_uuid: str, ticket_uuid: str, run_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "tickets", ticket_uuid, "runs", run_uuid),
        )

    def list_run_events(
        self,
        team_uuid: str,
        ticket_uuid: str,
        run_uuid: str,
    ) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(
                team_uuid,
                "tickets",
                ticket_uuid,
                "runs",
                run_uuid,
                "events",
            ),
        )
