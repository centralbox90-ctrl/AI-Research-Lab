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


@pytest.mark.anyio
async def test_gets_repository_backed_artifact_through_mcp(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    artifact = {
        "artifact_type": "market_research",
        "result": {
            "id": "result-001",
        },
    }
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    store.save(
        result_id="result-001",
        serialized_cycle=artifact,
    )

    server = build_research_mcp_server(
        db_path=database_path,
    )

    async with Client(
        server,
        raise_exceptions=True,
    ) as client:
        result = await client.call_tool(
            "get_research_artifact",
            {
                "result_id": "result-001",
            },
        )

    assert result.is_error is False
    assert result.structured_content == {
        "schema_version": 1,
        "result_id": "result-001",
        "artifact": artifact,
    }
@pytest.mark.anyio
async def test_compares_repository_backed_artifacts_through_mcp(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    store.save(
        result_id="result-001",
        serialized_cycle={
            "metadata": {
                "artifact_id": "artifact-001",
            },
            "specification": {
                "hypothesis_title": (
                    "Previous hypothesis"
                ),
                "hypothesis_description": (
                    "Previous hypothesis"
                ),
            },
            "cycle": {
                "result": {
                    "id": "result-001",
                },
                "evidence": {
                    "data": {
                        "net_profit": 1.0,
                    },
                },
                "evidence_strength_evaluation": {
                    "score": 0.4,
                },
            },
        },
    )
    store.save(
        result_id="result-002",
        serialized_cycle={
            "metadata": {
                "artifact_id": "artifact-002",
            },
            "specification": {
                "hypothesis_title": (
                    "Current hypothesis"
                ),
                "hypothesis_description": (
                    "Current hypothesis"
                ),
            },
            "cycle": {
                "result": {
                    "id": "result-002",
                },
                "evidence": {
                    "data": {
                        "net_profit": 2.5,
                    },
                },
                "evidence_strength_evaluation": {
                    "score": 0.7,
                },
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
            "compare_research_artifacts",
            {
                "artifact_a_result_id": "result-001",
                "artifact_b_result_id": "result-002",
            },
        )

    assert result.is_error is False

    payload = result.structured_content

    assert payload is not None
    assert payload["schema_version"] == 1
    assert payload["artifact_a_result_id"] == (
        "result-001"
    )
    assert payload["artifact_b_result_id"] == (
        "result-002"
    )
    assert payload["comparison"]["artifact_a_id"] == (
        "artifact-001"
    )
    assert payload["comparison"]["artifact_b_id"] == (
        "artifact-002"
    )
    assert (
        payload["comparison"]
        ["evidence_evolution"]
        ["metric_deltas"][0]
        ["absolute_delta"]
        == 1.5
    )
    assert (
        payload["comparison"]
        ["confidence_evolution"]
        ["current_confidence"]
        == 0.7
    )
