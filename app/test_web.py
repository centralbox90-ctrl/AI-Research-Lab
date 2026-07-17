from pathlib import Path
from typing import Any

import pytest

from app.web import (
    build_artifact_details,
    build_artifact_index,
    build_artifact_summary,
    build_lineage_tree,
    build_web_app,
    create_app,
    filter_artifacts,
    normalize_history,
)
from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)
from src.storage import SqliteResearchCycleStore


class FakeStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-001",
            "result-002",
        ]


class FakeLineageStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-parent",
            "result-child",
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


class FakeStoredResearchArtifactComparer:
    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ):
        assert artifact_a_result_id == "result-001"
        assert artifact_b_result_id == "result-002"

        return ArtifactComparisonFactory().create(
            artifact_a_id="artifact-001",
            artifact_b_id="artifact-002",
            previous_hypothesis=(
                "Williams predicts reversal."
            ),
            current_hypothesis=(
                "Williams plus ADX predicts reversal."
            ),
            hypothesis_change_reason=(
                "Hypothesis changed between research artifacts."
            ),
            previous_evidence={
                "net_profit": -11.17,
                "win_rate": 35.71,
                "total_trades": 42,
                "market": "BTCUSDT",
                "removed_metric": 10,
            },
            current_evidence={
                "net_profit": -8.64,
                "win_rate": 33.33,
                "total_trades": 42,
                "market": "ETHUSDT",
                "added_metric": 20,
            },
            evidence_change_reason=(
                "Evidence changed between research artifacts."
            ),
            previous_confidence=0.41995,
            current_confidence=0.418,
            confidence_change_reason=(
                "Confidence decreased."
            ),
        )


class MissingStoredResearchArtifactComparer:
    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ):
        raise ValueError(
            "Research artifact was not found for result_id: "
            f"{artifact_b_result_id}"
        )


def build_artifact(
    *,
    artifact_id: str = "artifact-001",
    parent_artifact_id: str | None = None,
    hypothesis: str = "Williams predicts reversal.",
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    confidence: float = 0.41995,
    created_at: str = "2026-07-15T18:00:00+00:00",
    lineage_type: str = "root",
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
            "question_description": (
                "Can Williams identify short-term reversal?"
            ),
            "hypothesis_description": hypothesis,
            "expected_result": (
                "Oversold values precede price recovery."
            ),
            "experiment_description": (
                "Backtest Williams reversal signals."
            ),
            "symbol": symbol,
            "timeframe": timeframe,
        },
        "cycle": {
            "evidence": {
                "data": {
                    "net_profit": -11.17,
                    "win_rate": 35.71,
                    "total_trades": 42,
                    "market": symbol,
                },
            },
            "evaluation": {
                "is_valid": True,
                "evidence_strength": "moderate",
                "warnings": [
                    "Drawdown remains elevated.",
                ],
            },
            "statistical_evaluation": {
                "is_evaluated": True,
                "sample_size": 42,
                "mean": -0.26595238095238094,
                "standard_deviation": 1.23456789,
                "standard_error": 0.1905,
                "confidence_interval_lower": -0.6393,
                "confidence_interval_upper": 0.1074,
                "confidence_level": 0.95,
                "is_significant": False,
                "p_value": 0.1642,
                "effect_size": -0.2154,
                "warnings": [
                    "Sample size is limited.",
                ],
            },
            "evidence_strength_evaluation": {
                "score": confidence,
                "level": "moderate",
                "is_evaluated": True,
                "warnings": [
                    "Evidence is not yet robust.",
                ],
            },
            "hypothesis_decision": {
                "decision": "continue_research",
                "supported": False,
                "confidence": confidence,
                "reason": (
                    "Evidence is insufficient for confirmation."
                ),
                "failed_requirements": [
                    "Minimum confidence threshold was not reached.",
                ],
                "warnings": [
                    "Additional validation is required.",
                ],
            },
            "conclusion": {
                "statement": (
                    "The hypothesis remains unconfirmed."
                ),
                "supported": False,
                "confidence": confidence,
                "is_provisional": True,
                "basis": (
                    "Current evidence is inconclusive."
                ),
            },
            "next_experiment_selection": {
                "is_selected": True,
                "action": "run_robustness_test",
                "priority": "high",
                "reason": (
                    "Robustness across regimes is unknown."
                ),
                "target_requirement": (
                    "Validate across multiple regimes."
                ),
                "recommendations": [
                    "Test additional symbols.",
                ],
                "warnings": [
                    "Do not promote the hypothesis yet.",
                ],
            },
        },
        "lineage": {
            "parent_artifact_id": parent_artifact_id,
            "lineage_type": lineage_type,
            "change_description": (
                "Research hypothesis was refined."
            ),
            "created_from_experiment": "experiment-001",
        },
        "history": [
            {
                "artifact_id": artifact_id,
                "previous_artifact_id": parent_artifact_id,
                "event_type": "artifact_created",
                "description": (
                    "Research artifact was created."
                ),
                "created_at": created_at,
            },
        ],
    }


def build_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "result-001": build_artifact(
            artifact_id="artifact-001",
            symbol="BTCUSDT",
            timeframe="1h",
            lineage_type="root",
        ),
        "result-002": build_artifact(
            artifact_id="artifact-002",
            parent_artifact_id="artifact-001",
            hypothesis=(
                "Williams plus ADX predicts reversal."
            ),
            symbol="ETHUSDT",
            timeframe="4h",
            confidence=0.72,
            created_at="2026-07-16T10:30:00+00:00",
            lineage_type="feature_extension",
        ),
    }


def test_build_artifact_summary_returns_context():

    summary = build_artifact_summary(
        result_id="result-001",
        artifact=build_artifacts()["result-001"],
    )

    assert summary["result_id"] == "result-001"
    assert summary["artifact_id"] == "artifact-001"
    assert summary["symbol"] == "BTCUSDT"
    assert summary["timeframe"] == "1h"
    assert summary["confidence"] == 0.41995
    assert summary["lineage_type"] == "root"


def test_build_artifact_summary_handles_missing():

    summary = build_artifact_summary(
        result_id="missing",
        artifact=None,
    )

    assert summary["artifact_id"] is None
    assert summary["symbol"] == "Unknown symbol"
    assert summary["confidence"] is None


def test_build_artifact_index_resolves_lineage():

    artifacts = build_artifacts()

    index = build_artifact_index(
        result_ids=[
            "result-001",
            "result-002",
        ],
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts,
        ),
    )

    assert index[0]["depth"] == 0
    assert index[1]["depth"] == 1
    assert index[1]["parent_result_id"] == "result-001"


@pytest.mark.parametrize(
    (
        "filters",
        "expected_result_id",
    ),
    [
        (
            {"symbol": "btc"},
            "result-001",
        ),
        (
            {"timeframe": "4H"},
            "result-002",
        ),
        (
            {"hypothesis": "plus adx"},
            "result-002",
        ),
        (
            {"lineage_type": "extension"},
            "result-002",
        ),
    ],
)
def test_filter_artifacts(
    filters: dict[str, str],
    expected_result_id: str,
):

    index = build_artifact_index(
        result_ids=[
            "result-001",
            "result-002",
        ],
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    filtered = filter_artifacts(
        artifacts=index,
        **filters,
    )

    assert len(filtered) == 1
    assert filtered[0]["result_id"] == expected_result_id


def test_filter_artifacts_combines_filters():

    index = build_artifact_index(
        result_ids=[
            "result-001",
            "result-002",
        ],
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    filtered = filter_artifacts(
        artifacts=index,
        symbol="ETH",
        timeframe="4h",
        hypothesis="ADX",
        lineage_type="extension",
    )

    assert [
        artifact["result_id"]
        for artifact in filtered
    ] == [
        "result-002",
    ]


def test_build_lineage_tree_returns_nested_tree():

    index = build_artifact_index(
        result_ids=[
            "result-001",
            "result-002",
        ],
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    tree, orphans = build_lineage_tree(index)

    assert orphans == []
    assert len(tree) == 1
    assert tree[0]["artifact_id"] == "artifact-001"
    assert tree[0]["children"][0]["artifact_id"] == (
        "artifact-002"
    )


def test_build_lineage_tree_returns_orphan():

    orphan = build_artifact_summary(
        result_id="result-orphan",
        artifact=build_artifact(
            artifact_id="artifact-orphan",
            parent_artifact_id="missing-parent",
        ),
    )

    tree, orphans = build_lineage_tree([orphan])

    assert tree == []
    assert orphans[0]["artifact_id"] == "artifact-orphan"


def test_normalize_history_ignores_invalid_entries():

    history = normalize_history(
        [
            {
                "artifact_id": "artifact-001",
                "event_type": "artifact_created",
            },
            "invalid",
        ]
    )

    assert len(history) == 1
    assert history[0]["artifact_id"] == "artifact-001"


def test_build_artifact_details_returns_research_data():

    details = build_artifact_details(
        result_id="result-001",
        artifact=build_artifacts()["result-001"],
    )

    assert details["artifact_id"] == "artifact-001"
    assert details["question"] == (
        "Can Williams identify short-term reversal?"
    )
    assert details["evidence_metrics"]["net_profit"] == -11.17
    assert details["evidence_strength_score"] == 0.41995
    assert details["hypothesis_decision"] == (
        "continue_research"
    )
    assert details["next_experiment_action"] == (
        "run_robustness_test"
    )


def test_web_index_returns_ui_shell():

    app = create_app()
    response = app.test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "AI Research Lab" in body
    assert "Filter and sort research artifacts" in body
    assert "Compare research artifacts" in body
    assert "Research lineage tree" in body
    assert "No stored research artifacts." in body


def test_web_index_lists_artifacts():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    response = app.test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "BTCUSDT" in body
    assert "ETHUSDT" in body
    assert "artifact-001" in body
    assert "artifact-002" in body
    assert 'href="/artifacts/result-001"' in body
    assert 'href="/artifacts/result-002"' in body


@pytest.mark.parametrize(
    (
        "query",
        "expected_text",
        "excluded_text",
    ),
    [
        (
            "?symbol=BTC",
            "Williams predicts reversal.",
            "Williams plus ADX predicts reversal.",
        ),
        (
            "?timeframe=4h",
            "Williams plus ADX predicts reversal.",
            "Williams predicts reversal.",
        ),
        (
            "?hypothesis=plus+ADX",
            "Williams plus ADX predicts reversal.",
            "Williams predicts reversal.",
        ),
    ],
)
def test_web_index_filters_artifacts(
    query: str,
    expected_text: str,
    excluded_text: str,
):

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    body = app.test_client().get(
        f"/{query}"
    ).get_data(
        as_text=True,
    )

    assert "Showing 1 of 2 research artifacts." in body
    assert expected_text in body
    assert excluded_text not in body


def test_web_index_shows_empty_filter_result():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    body = app.test_client().get(
        "/?symbol=SOLUSDT"
    ).get_data(
        as_text=True,
    )

    assert "Showing 0 of 2 research artifacts." in body

    assert (
        "No research artifacts match the active filters."
        in body
    )


def test_web_artifact_details_returns_artifact():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            build_artifacts(),
        ),
    )

    response = app.test_client().get(
        "/artifacts/result-001"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Artifact identity" in body
    assert "Research lineage" in body
    assert "Artifact history" in body
    assert "Evidence metrics" in body
    assert "Hypothesis decision" in body
    assert "Next research action" in body
    assert "artifact-002" in body


def test_web_artifact_details_returns_not_found():

    app = create_app(
        artifact_getter=FakeStoredResearchArtifactGetter(
            {},
        ),
    )

    response = app.test_client().get(
        "/artifacts/missing"
    )

    assert response.status_code == 404


def test_web_comparison_requires_both_ids():

    app = create_app(
        artifact_comparer=(
            FakeStoredResearchArtifactComparer()
        ),
    )

    response = app.test_client().get(
        "/compare?artifact_a_result_id=result-001"
    )

    assert response.status_code == 400

    assert (
        "Both artifact result IDs are required."
        in response.get_data(as_text=True)
    )


def test_web_comparison_returns_not_found():

    app = create_app(
        artifact_comparer=(
            MissingStoredResearchArtifactComparer()
        ),
    )

    response = app.test_client().get(
        "/compare"
        "?artifact_a_result_id=result-001"
        "&artifact_b_result_id=missing"
    )

    assert response.status_code == 404
    assert "missing" in response.get_data(as_text=True)


def test_web_comparison_renders_metric_deltas():

    app = create_app(
        artifact_comparer=(
            FakeStoredResearchArtifactComparer()
        ),
    )

    response = app.test_client().get(
        "/compare"
        "?artifact_a_result_id=result-001"
        "&artifact_b_result_id=result-002"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "artifact-001" in body
    assert "artifact-002" in body
    assert "net_profit" in body
    assert "2.53" in body
    assert "2.5299999999999994" not in body
    assert "-2.38" in body
    assert "added_metric" in body
    assert "removed_metric" in body
    assert "Not comparable" in body
    assert "Confidence decreased." in body


def test_build_web_app_reads_persisted_artifacts(
    tmp_path: Path,
):

    database_path = tmp_path / "research.db"

    store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    artifacts = build_artifacts()

    store.save(
        result_id="result-001",
        serialized_cycle=artifacts["result-001"],
    )

    store.save(
        result_id="result-002",
        serialized_cycle=artifacts["result-002"],
    )

    app = build_web_app(
        db_path=database_path,
    )

    client = app.test_client()

    index_response = client.get("/")

    assert index_response.status_code == 200

    index_body = index_response.get_data(
        as_text=True,
    )

    assert "artifact-001" in index_body
    assert "artifact-002" in index_body
    assert "Research lineage tree" in index_body

    details_response = client.get(
        "/artifacts/result-002"
    )

    assert details_response.status_code == 200
    assert "artifact-002" in details_response.get_data(
        as_text=True,
    )