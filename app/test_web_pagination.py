from typing import Any

from app.web import (
    create_app,
    paginate_artifacts,
)


class FakeStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-001",
            "result-002",
            "result-003",
            "result-004",
            "result-005",
            "result-006",
        ]


class FakeStoredResearchArtifactGetter:
    def __init__(
        self,
        artifacts: dict[str, dict[str, Any]],
    ) -> None:
        self.artifacts = artifacts

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        return self.artifacts.get(result_id)


def build_artifact(
    *,
    artifact_id: str,
    symbol: str,
    created_at: str,
    confidence: float,
) -> dict[str, Any]:
    return {
        "artifact_version": 1,
        "metadata": {
            "artifact_id": artifact_id,
            "created_at": created_at,
            "executor_type": "market_backtest",
            "data_source": "historical",
        },
        "specification": {
            "hypothesis_description": (
                f"Hypothesis for {symbol}"
            ),
            "symbol": symbol,
            "timeframe": "1h",
        },
        "cycle": {
            "evidence_strength_evaluation": {
                "score": confidence,
            },
        },
        "lineage": {
            "parent_artifact_id": None,
            "lineage_type": "root",
        },
    }


def build_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "result-001": build_artifact(
            artifact_id="artifact-001",
            symbol="BTCUSDT",
            created_at="2026-07-01T10:00:00+00:00",
            confidence=0.1,
        ),
        "result-002": build_artifact(
            artifact_id="artifact-002",
            symbol="ETHUSDT",
            created_at="2026-07-02T10:00:00+00:00",
            confidence=0.2,
        ),
        "result-003": build_artifact(
            artifact_id="artifact-003",
            symbol="ADAUSDT",
            created_at="2026-07-03T10:00:00+00:00",
            confidence=0.3,
        ),
        "result-004": build_artifact(
            artifact_id="artifact-004",
            symbol="SOLUSDT",
            created_at="2026-07-04T10:00:00+00:00",
            confidence=0.4,
        ),
        "result-005": build_artifact(
            artifact_id="artifact-005",
            symbol="XRPUSDT",
            created_at="2026-07-05T10:00:00+00:00",
            confidence=0.5,
        ),
        "result-006": build_artifact(
            artifact_id="artifact-006",
            symbol="BNBUSDT",
            created_at="2026-07-06T10:00:00+00:00",
            confidence=0.6,
        ),
    }


def build_summaries(
    count: int,
) -> list[dict[str, Any]]:
    return [
        {
            "result_id": f"result-{index:03d}",
            "artifact_id": f"artifact-{index:03d}",
            "parent_artifact_id": None,
            "parent_result_id": None,
            "lineage_type": "root",
            "depth": 0,
            "symbol": f"SYMBOL{index}",
            "timeframe": "1h",
            "hypothesis": f"Hypothesis {index}",
            "confidence": index / 10,
            "created_at": (
                f"2026-07-{index:02d}T10:00:00+00:00"
            ),
        }
        for index in range(1, count + 1)
    ]


def extract_research_artifact_section(
    body: str,
) -> str:
    section_start = body.rfind(
        "<h2>Research artifacts</h2>"
    )

    assert section_start != -1

    return body[
        section_start:
    ]


def test_paginate_artifacts_returns_first_page():

    artifacts = build_summaries(
        6,
    )

    pagination = paginate_artifacts(
        artifacts=artifacts,
        page=1,
        page_size=5,
    )

    assert [
        artifact["result_id"]
        for artifact in pagination["items"]
    ] == [
        "result-001",
        "result-002",
        "result-003",
        "result-004",
        "result-005",
    ]

    assert pagination["page"] == 1
    assert pagination["page_size"] == 5
    assert pagination["total_items"] == 6
    assert pagination["total_pages"] == 2
    assert pagination["has_previous"] is False
    assert pagination["has_next"] is True
    assert pagination["previous_page"] is None
    assert pagination["next_page"] == 2


def test_paginate_artifacts_returns_second_page():

    artifacts = build_summaries(
        6,
    )

    pagination = paginate_artifacts(
        artifacts=artifacts,
        page=2,
        page_size=5,
    )

    assert [
        artifact["result_id"]
        for artifact in pagination["items"]
    ] == [
        "result-006",
    ]

    assert pagination["page"] == 2
    assert pagination["total_pages"] == 2
    assert pagination["has_previous"] is True
    assert pagination["has_next"] is False
    assert pagination["previous_page"] == 1
    assert pagination["next_page"] is None


def test_paginate_artifacts_normalizes_low_page():

    pagination = paginate_artifacts(
        artifacts=build_summaries(6),
        page=0,
        page_size=5,
    )

    assert pagination["page"] == 1


def test_paginate_artifacts_normalizes_high_page():

    pagination = paginate_artifacts(
        artifacts=build_summaries(6),
        page=99,
        page_size=5,
    )

    assert pagination["page"] == 2

    assert [
        artifact["result_id"]
        for artifact in pagination["items"]
    ] == [
        "result-006",
    ]


def test_paginate_artifacts_normalizes_page_size():

    pagination = paginate_artifacts(
        artifacts=build_summaries(3),
        page=1,
        page_size=0,
    )

    assert pagination["page_size"] == 1
    assert pagination["total_pages"] == 3
    assert len(pagination["items"]) == 1


def test_paginate_artifacts_handles_empty_list():

    pagination = paginate_artifacts(
        artifacts=[],
        page=1,
        page_size=5,
    )

    assert pagination["items"] == []
    assert pagination["page"] == 1
    assert pagination["total_items"] == 0
    assert pagination["total_pages"] == 1
    assert pagination["has_previous"] is False
    assert pagination["has_next"] is False


def test_web_index_renders_first_page():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/?page=1&page_size=5"
        "&sort_by=created_at"
        "&sort_direction=ascending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    section = extract_research_artifact_section(
        body,
    )

    assert "result-001" in section
    assert "result-002" in section
    assert "result-003" in section
    assert "result-004" in section
    assert "result-005" in section
    assert "result-006" not in section

    assert "Page 1" in body
    assert "of 2" in body
    assert "Next page" in body
    assert "Previous page" not in body


def test_web_index_renders_second_page():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/?page=2&page_size=5"
        "&sort_by=created_at"
        "&sort_direction=ascending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    section = extract_research_artifact_section(
        body,
    )

    assert "result-006" in section
    assert "result-001" not in section
    assert "result-002" not in section
    assert "result-003" not in section
    assert "result-004" not in section
    assert "result-005" not in section

    assert "Page 2" in body
    assert "of 2" in body
    assert "Previous page" in body
    assert "Next page" not in body


def test_web_index_preserves_query_parameters_in_next_link():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/?symbol=USDT"
        "&timeframe=1h"
        "&hypothesis=Hypothesis"
        "&lineage_type=root"
        "&sort_by=confidence"
        "&sort_direction=ascending"
        "&page=1"
        "&page_size=5"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert "Next page" in body
    assert "symbol=USDT" in body
    assert "timeframe=1h" in body
    assert "hypothesis=Hypothesis" in body
    assert "lineage_type=root" in body
    assert "sort_by=confidence" in body
    assert "sort_direction=ascending" in body
    assert "page=2" in body
    assert "page_size=5" in body


def test_web_index_falls_back_for_invalid_page():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/?page=invalid&page_size=invalid"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert "Page 1" in body
    assert "of 1" in body


def test_web_index_falls_back_for_disallowed_page_size():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/?page=1&page_size=999"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert 'value="10"' in body
    assert "Page 1" in body
    assert "of 1" in body