from __future__ import annotations

from typing import Any, TypedDict

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from src.application.public_api import (
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


def create_research_mcp_server(
    *,
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

    return server
