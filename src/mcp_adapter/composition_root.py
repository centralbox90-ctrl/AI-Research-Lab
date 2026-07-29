from __future__ import annotations

from pathlib import Path

from mcp.server import MCPServer

from src.application.public_api import (
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
    list_stored_research_cycles = (
        ListStoredResearchCycles(
            store=store,
        )
    )

    return create_research_mcp_server(
        list_stored_research_cycles=(
            list_stored_research_cycles
        ),
    )
