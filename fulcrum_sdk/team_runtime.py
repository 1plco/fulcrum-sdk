"""Team runtime client for Fulcrum v1 orchestration endpoints."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class TeamRuntimeResource(BaseResource):
    """Client for team-ticket runtime-only orchestration endpoints."""

    def context(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "runtime", "context"))

    def submit_graph(self, team_uuid: str, draft: JsonDict) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs"),
            json={"draft": draft},
        )

    def request_approval(
        self,
        team_uuid: str,
        *,
        graph_uuid: str,
        prompt: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "approvals"),
            json=self._clean_params(graphUuid=graph_uuid, prompt=prompt),
        )

    def get_approval(self, team_uuid: str, approval_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "runtime", "approvals", approval_uuid),
        )

    def append_graph_event(
        self,
        team_uuid: str,
        graph_uuid: str,
        *,
        event_id: str,
        event_type: str,
        status: str,
        event_ts: str | None = None,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs", graph_uuid, "events"),
            json=self._clean_params(
                eventId=event_id,
                eventTs=event_ts,
                eventType=event_type,
                payload=payload,
                status=status,
            ),
        )

    def create_checkpoint(
        self,
        team_uuid: str,
        checkpoint: JsonDict,
        *,
        reason: str,
        summary: str,
        graph_uuid: str | None = None,
        runtime_execution_uuid: str | None = None,
        sandbox_id: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "checkpoints"),
            json=self._clean_params(
                checkpoint=checkpoint,
                graphUuid=graph_uuid,
                reason=reason,
                runtimeExecutionUuid=runtime_execution_uuid,
                sandboxId=sandbox_id,
                summary=summary,
            ),
        )

    def create_artifact(
        self,
        team_uuid: str,
        *,
        content: JsonDict,
        graph_uuid: str,
        kind: str,
        summary: str,
        artifact_refs: list[JsonDict] | None = None,
        content_schema: JsonDict | None = None,
        data_classes: list[str] | None = None,
        graph_node_uuid: str | None = None,
        node_attempt_uuid: str | None = None,
        provenance: JsonDict | None = None,
        redaction: JsonDict | None = None,
        schema_id: str | None = None,
        schema_version: int | None = None,
        source_artifact_hashes: JsonDict | None = None,
        source_artifact_uuids: list[str] | None = None,
        token_estimate: int | None = None,
        validation: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "artifacts"),
            json=self._clean_params(
                artifactRefs=artifact_refs,
                content=content,
                contentSchema=content_schema,
                dataClasses=data_classes,
                graphNodeUuid=graph_node_uuid,
                graphUuid=graph_uuid,
                kind=kind,
                nodeAttemptUuid=node_attempt_uuid,
                provenance=provenance,
                redaction=redaction,
                schemaId=schema_id,
                schemaVersion=schema_version,
                sourceArtifactHashes=source_artifact_hashes,
                sourceArtifactUuids=source_artifact_uuids,
                summary=summary,
                tokenEstimate=token_estimate,
                validation=validation,
            ),
        )

    def get_artifact(self, team_uuid: str, artifact_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "runtime", "artifacts", artifact_uuid),
        )

    def create_context_package(
        self,
        team_uuid: str,
        node_uuid: str,
        *,
        source_artifact_uuids: list[str] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(
                team_uuid,
                "runtime",
                "nodes",
                node_uuid,
                "context-package",
            ),
            json=self._clean_params(sourceArtifactUuids=source_artifact_uuids),
        )

    def claim_ready_nodes(
        self,
        team_uuid: str,
        graph_uuid: str,
        *,
        idempotency_key: str | None = None,
        limit: int | None = None,
        source_artifact_uuids_by_node_uuid: dict[str, list[str]] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(
                team_uuid,
                "runtime",
                "graphs",
                graph_uuid,
                "nodes",
                "claim-ready",
            ),
            json=self._clean_params(
                idempotencyKey=idempotency_key,
                limit=limit,
                sourceArtifactUuidsByNodeUuid=source_artifact_uuids_by_node_uuid,
            ),
        )
