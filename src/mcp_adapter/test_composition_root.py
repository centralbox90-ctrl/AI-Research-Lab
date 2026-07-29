from pathlib import Path

import pytest
from mcp import Client

from src.mcp_adapter import (
    build_research_mcp_server,
)
from src.storage import (
    SqliteResearchCycleStore,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_builds_repository_backed_mcp_server(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    store.save(
        result_id="result-002",
        serialized_cycle={
            "result": {
                "id": "result-002",
            },
        },
    )
    store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
            },
        },
    )

    server = build_research_mcp_server(
        db_path=database_path,
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "list_research_cycles",
            {},
        )

    assert result.is_error is False
    assert result.structured_content == {
        "schema_version": 1,
        "count": 2,
        "result_ids": [
            "result-001",
            "result-002",
        ],
    }


@pytest.mark.anyio
async def test_builds_mcp_server_with_empty_database(
    tmp_path: Path,
) -> None:
    server = build_research_mcp_server(
        db_path=(
            tmp_path / "research-cycles.db"
        ),
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "list_research_cycles",
            {},
        )

    assert result.is_error is False
    assert result.structured_content == {
        "schema_version": 1,
        "count": 0,
        "result_ids": [],
    }
