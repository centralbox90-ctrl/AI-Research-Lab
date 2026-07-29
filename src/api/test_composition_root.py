from pathlib import Path

from src.api import build_research_api
from src.storage import (
    SqliteResearchCycleStore,
)


def test_builds_repository_backed_research_api(
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

    application = build_research_api(
        db_path=database_path,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "schema_version": 1,
        "count": 2,
        "result_ids": [
            "result-001",
            "result-002",
        ],
    }


def test_builds_api_with_empty_database(
    tmp_path: Path,
) -> None:
    application = build_research_api(
        db_path=(
            tmp_path / "research-cycles.db"
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "schema_version": 1,
        "count": 0,
        "result_ids": [],
    }