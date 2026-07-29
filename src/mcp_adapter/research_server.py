from __future__ import annotations

from typing import Any, TypedDict

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from src.application.public_api import (
    CompareStoredResearchArtifacts,
    GetStoredResearchArtifact,
    ListStoredResearchCycles,
)


class ResearchCycleListResult(TypedDict):
    schema_version: int
    count: int
    result_ids: list[str]


class ResearchArtifactResult(TypedDict):
    schema_version: int
    result_id: str
    artifact: dict[str, Any]


class ArtifactComparisonResult(TypedDict):
    schema_version: int
    artifact_a_result_id: str
    artifact_b_result_id: str
    comparison: dict[str, Any]


def create_research_mcp_server(
    *,
    compare_stored_research_artifacts: (
        CompareStoredResearchArtifacts
    ),
    get_stored_research_artifact: (
        GetStoredResearchArtifact
    ),
    list_stored_research_cycles: (
        ListStoredResearchCycles
    ),
) -> MCPServer:
    """
    Create the MCP adapter for public research use cases.

    The adapter owns MCP tool registration and transport DTO
    rendering. Persistence and Application composition remain
    outside this module.
    """

    if not callable(
        getattr(
            compare_stored_research_artifacts,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "compare_stored_research_artifacts must "
            "provide a callable execute method"
        )

    if not callable(
        getattr(
            get_stored_research_artifact,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "get_stored_research_artifact must provide "
            "a callable execute method"
        )

    if not callable(
        getattr(
            list_stored_research_cycles,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "list_stored_research_cycles must provide "
            "a callable execute method"
        )

    server = MCPServer(
        name="ai-research-lab",
        title="AI Research Lab",
        description=(
            "Read-only access to stored "
            "research results."
        ),
        instructions=(
            "Use read-only tools to inspect stored "
            "AI Research Lab results."
        ),
        version="1.0.0",
    )

    @server.tool(
        name="list_research_cycles",
        title="List research cycles",
        description=(
            "List identifiers of stored research cycles "
            "in deterministic order."
        ),
        annotations=ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    def list_research_cycles(
    ) -> ResearchCycleListResult:
        result_ids = (
            list_stored_research_cycles.execute()
        )

        if not isinstance(result_ids, list):
            raise TypeError(
                "ListStoredResearchCycles must return "
                "a list"
            )

        if not all(
            isinstance(result_id, str)
            for result_id in result_ids
        ):
            raise TypeError(
                "research cycle identifiers "
                "must be strings"
            )

        return {
            "schema_version": 1,
            "count": len(result_ids),
            "result_ids": list(result_ids),
        }

    @server.tool(
        name="get_research_artifact",
        title="Get research artifact",
        description=(
            "Retrieve one stored research artifact "
            "by its result identifier."
        ),
        annotations=ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    def get_research_artifact(
        result_id: str,
    ) -> ResearchArtifactResult:
        if not result_id.strip():
            raise ValueError(
                "result_id must not be empty"
            )

        normalized_result_id = result_id.strip()
        artifact = (
            get_stored_research_artifact.execute(
                normalized_result_id
            )
        )

        if artifact is None:
            raise ValueError(
                "Research artifact not found: "
                + normalized_result_id
            )

        if not isinstance(artifact, dict):
            raise TypeError(
                "GetStoredResearchArtifact must return "
                "a dictionary or None"
            )

        return {
            "schema_version": 1,
            "result_id": normalized_result_id,
            "artifact": dict(artifact),
        }

    @server.tool(
        name="compare_research_artifacts",
        title="Compare research artifacts",
        description=(
            "Compare hypothesis, evidence, and confidence "
            "between two stored research artifacts."
        ),
        annotations=ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    def compare_research_artifacts(
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ) -> ArtifactComparisonResult:
        normalized_artifact_a_result_id = (
            artifact_a_result_id.strip()
        )
        normalized_artifact_b_result_id = (
            artifact_b_result_id.strip()
        )

        if (
            not normalized_artifact_a_result_id
            or not normalized_artifact_b_result_id
        ):
            raise ValueError(
                "artifact_a_result_id and "
                "artifact_b_result_id must not be empty"
            )

        comparison = (
            compare_stored_research_artifacts.execute(
                artifact_a_result_id=(
                    normalized_artifact_a_result_id
                ),
                artifact_b_result_id=(
                    normalized_artifact_b_result_id
                ),
            )
        )

        return {
            "schema_version": 1,
            "artifact_a_result_id": (
                normalized_artifact_a_result_id
            ),
            "artifact_b_result_id": (
                normalized_artifact_b_result_id
            ),
            "comparison": {
                "artifact_a_id": comparison.artifact_a_id,
                "artifact_b_id": comparison.artifact_b_id,
                "hypothesis_evolution": {
                    "previous_hypothesis": (
                        comparison
                        .hypothesis_evolution
                        .previous_hypothesis
                    ),
                    "current_hypothesis": (
                        comparison
                        .hypothesis_evolution
                        .current_hypothesis
                    ),
                    "change_reason": (
                        comparison
                        .hypothesis_evolution
                        .change_reason
                    ),
                },
                "evidence_evolution": {
                    "previous_evidence": (
                        comparison
                        .evidence_evolution
                        .previous_evidence
                    ),
                    "current_evidence": (
                        comparison
                        .evidence_evolution
                        .current_evidence
                    ),
                    "metric_deltas": [
                        {
                            "metric_name": delta.metric_name,
                            "previous_value": (
                                delta.previous_value
                            ),
                            "current_value": (
                                delta.current_value
                            ),
                            "absolute_delta": (
                                delta.absolute_delta
                            ),
                            "direction": delta.direction,
                        }
                        for delta in (
                            comparison
                            .evidence_evolution
                            .metric_deltas
                        )
                    ],
                    "change_reason": (
                        comparison
                        .evidence_evolution
                        .change_reason
                    ),
                },
                "confidence_evolution": {
                    "previous_confidence": (
                        comparison
                        .confidence_evolution
                        .previous_confidence
                    ),
                    "current_confidence": (
                        comparison
                        .confidence_evolution
                        .current_confidence
                    ),
                    "change_reason": (
                        comparison
                        .confidence_evolution
                        .change_reason
                    ),
                },
            },
        }

    return server
