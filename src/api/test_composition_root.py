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

    artifact_response = client.get(
        "/v1/research-artifacts/result-001"
    )

    assert artifact_response.status_code == 200
    assert artifact_response.get_json() == {
        "schema_version": 1,
        "result_id": "result-001",
        "artifact": {
            "result": {
                "id": "result-001",
            },
        },
    }


def test_builds_api_with_bearer_authentication(
    tmp_path: Path,
) -> None:
    application = build_research_api(
        db_path=(
            tmp_path / "research-cycles.db"
        ),
        api_token=(
            "private-api-token-value"
        ),
    )
    client = application.test_client()

    unauthorized_response = client.get(
        "/v1/research-cycles"
    )

    assert unauthorized_response.status_code == 401

    authorized_response = client.get(
        "/v1/research-cycles",
        headers={
            "Authorization": (
                "Bearer private-api-token-value"
            ),
        },
    )

    assert authorized_response.status_code == 200
    assert authorized_response.get_json() == {
        "schema_version": 1,
        "count": 0,
        "result_ids": [],
    }

    openapi_response = client.get(
        "/openapi.json",
        headers={
            "Authorization": (
                "Bearer private-api-token-value"
            ),
        },
    )

    assert openapi_response.status_code == 200
    assert openapi_response.get_json()[
        "security"
    ] == [
        {
            "BearerAuth": [],
        },
    ]


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

    artifact_response = client.get(
        "/v1/research-artifacts/unknown-result"
    )

    assert artifact_response.status_code == 404
    assert artifact_response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": (
                "research_artifact_not_found"
            ),
            "message": (
                "Research artifact not found: "
                "unknown-result"
            ),
        },
    }

def test_builds_repository_backed_comparison(
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

    application = build_research_api(
        db_path=database_path,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifact-comparisons",
        query_string={
            "artifact_a_result_id": "result-001",
            "artifact_b_result_id": "result-002",
        },
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["comparison"]["artifact_a_id"] == (
        "artifact-001"
    )
    assert payload["comparison"]["artifact_b_id"] == (
        "artifact-002"
    )
    assert (
        payload["comparison"]
        ["confidence_evolution"]
        ["current_confidence"]
        == 0.7
    )
