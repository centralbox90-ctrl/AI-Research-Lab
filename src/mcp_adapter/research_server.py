from __future__ import annotations

from typing import TypedDict

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from src.application.public_api import (
    ListStoredResearchCycles,
)


class ResearchCycleListResult(TypedDict):
    schema_version: int
    count: int
    result_ids: list[str]


def create_research_mcp_server(
    *,
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

    return server
