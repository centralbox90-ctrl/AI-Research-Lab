from __future__ import annotations

from pathlib import Path

from mcp.server import MCPServer

from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.public_api import (
    CompareStoredResearchArtifacts,
    GetStoredResearchArtifact,
    ListStoredResearchCycles,
)
from src.mcp_adapter.research_server import (
    create_research_mcp_server,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


def build_research_mcp_server(
    db_path: str | Path = (
        RESEARCH_CYCLE_DATABASE_PATH
    ),
) -> MCPServer:
    """
    Build the production MCP dependency graph.

    Infrastructure is selected only in this composition root.
    """

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )
    get_stored_research_artifact = (
        GetStoredResearchArtifact(
            store=store,
        )
    )
    compare_stored_research_artifacts = (
        CompareStoredResearchArtifacts(
            artifact_getter=(
                get_stored_research_artifact
            ),
            input_extractor=(
                ArtifactComparisonInputExtractor()
            ),
        )
    )
    list_stored_research_cycles = (
        ListStoredResearchCycles(
            store=store,
        )
    )

    return create_research_mcp_server(
        compare_stored_research_artifacts=(
            compare_stored_research_artifacts
        ),
        get_stored_research_artifact=(
            get_stored_research_artifact
        ),
        list_stored_research_cycles=(
            list_stored_research_cycles
        ),
    )
