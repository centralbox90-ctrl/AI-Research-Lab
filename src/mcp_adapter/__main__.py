from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from src.mcp_adapter.composition_root import (
    build_research_mcp_server,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Run the local read-only MCP server over stdio.

    The MCP host owns the subprocess lifecycle and transport.
    """

    parser = argparse.ArgumentParser(
        prog="python -m src.mcp_adapter",
        description=(
            "Run the AI Research Lab MCP server "
            "over stdio."
        ),
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=RESEARCH_CYCLE_DATABASE_PATH,
        help=(
            "Path to the SQLite research "
            "database."
        ),
    )

    arguments = parser.parse_args(
        None
        if argv is None
        else list(argv)
    )

    server = build_research_mcp_server(
        db_path=arguments.database,
    )

    server.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
