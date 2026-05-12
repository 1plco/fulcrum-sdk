"""Team runtime client for Fulcrum v1 orchestration endpoints."""

from __future__ import annotations

from fulcrum_sdk._resource import BaseResource
from fulcrum_sdk.models import JsonDict


class TeamRuntimeResource(BaseResource):
    """Client for team-ticket runtime-only orchestration endpoints."""

    def _idempotency_headers(self, idempotency_key: str | None) -> dict[str, str] | None:
        if not idempotency_key:
            return None
        return {"Idempotency-Key": idempotency_key}

    def context(self, team_uuid: str) -> JsonDict:
        return self._request("GET", self._team_path(team_uuid, "runtime", "context"))

    def submit_graph(
        self,
        team_uuid: str,
        draft: JsonDict,
        *,
        idempotency_key: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(draft=draft, idempotencyKey=idempotency_key),
        )

    def get_graph(self, team_uuid: str, graph_uuid: str) -> JsonDict:
        return self._request(
            "GET",
            self._team_path(team_uuid, "runtime", "graphs", graph_uuid),
        )

    def request_approval(
        self,
        team_uuid: str,
        *,
        amendment_reason: str | None = None,
        approval_kind: str | None = None,
        base_graph_uuid: str | None = None,
        graph_uuid: str,
        idempotency_key: str | None = None,
        prompt: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "approvals"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                amendmentReason=amendment_reason,
                approvalKind=approval_kind,
                baseGraphUuid=base_graph_uuid,
                graphUuid=graph_uuid,
                idempotencyKey=idempotency_key,
                prompt=prompt,
            ),
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
        event_type: str,
        status: str,
        event_id: str | None = None,
        event_ts: str | None = None,
        idempotency_key: str | None = None,
        payload: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "graphs", graph_uuid, "events"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                eventId=event_id,
                eventTs=event_ts,
                eventType=event_type,
                idempotencyKey=idempotency_key,
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
        idempotency_key: str | None = None,
        runtime_execution_uuid: str | None = None,
        sandbox_id: str | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "checkpoints"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                checkpoint=checkpoint,
                graphUuid=graph_uuid,
                idempotencyKey=idempotency_key,
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
        idempotency_key: str | None = None,
        source_artifact_hashes: JsonDict | None = None,
        source_artifact_uuids: list[str] | None = None,
        token_estimate: int | None = None,
        validation: JsonDict | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "artifacts"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                artifactRefs=artifact_refs,
                content=content,
                contentSchema=content_schema,
                dataClasses=data_classes,
                graphNodeUuid=graph_node_uuid,
                graphUuid=graph_uuid,
                idempotencyKey=idempotency_key,
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
        allowed_node_types: list[str] | None = None,
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
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                allowedNodeTypes=allowed_node_types,
                idempotencyKey=idempotency_key,
                limit=limit,
                sourceArtifactUuidsByNodeUuid=source_artifact_uuids_by_node_uuid,
            ),
        )

    def update_node(
        self,
        team_uuid: str,
        node_uuid: str,
        *,
        attempt_uuid: str,
        status: str,
        error_message: str | None = None,
        idempotency_key: str | None = None,
        output_artifact_uuid: str | None = None,
        output_json: JsonDict | None = None,
        response_json: JsonDict | None = None,
        result_summary: str | None = None,
    ) -> JsonDict:
        return self._request(
            "PATCH",
            self._team_path(team_uuid, "runtime", "nodes", node_uuid),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                attemptUuid=attempt_uuid,
                errorMessage=error_message,
                idempotencyKey=idempotency_key,
                outputArtifactUuid=output_artifact_uuid,
                outputJson=output_json,
                responseJson=response_json,
                resultSummary=result_summary,
                status=status,
            ),
        )

    def create_node_attempt(
        self,
        team_uuid: str,
        node_uuid: str,
        *,
        graph_uuid: str,
        idempotency_key: str | None = None,
        source_artifact_uuids: list[str] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(team_uuid, "runtime", "nodes", node_uuid, "attempts"),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                graphUuid=graph_uuid,
                idempotencyKey=idempotency_key,
                sourceArtifactUuids=source_artifact_uuids,
            ),
        )

    def execute_project_ticket_node(
        self,
        team_uuid: str,
        node_uuid: str,
        *,
        graph_uuid: str,
        idempotency_key: str | None = None,
        source_artifact_uuids: list[str] | None = None,
    ) -> JsonDict:
        return self._request(
            "POST",
            self._team_path(
                team_uuid,
                "runtime",
                "nodes",
                node_uuid,
                "project-ticket",
            ),
            headers=self._idempotency_headers(idempotency_key),
            json=self._clean_params(
                graphUuid=graph_uuid,
                idempotencyKey=idempotency_key,
                sourceArtifactUuids=source_artifact_uuids,
            ),
        )
