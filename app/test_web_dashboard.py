from typing import Any

from app.web import (
    build_artifact_index,
    build_dashboard_statistics,
    create_app,
)


class FakeStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-root",
            "result-child",
            "result-orphan",
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
    parent_artifact_id: str | None,
    symbol: str,
    timeframe: str,
    confidence: float | None,
    lineage_type: str,
) -> dict[str, Any]:
    evidence_strength_evaluation: dict[str, Any] = {}

    if confidence is not None:
        evidence_strength_evaluation[
            "score"
        ] = confidence

    return {
        "artifact_version": 1,
        "metadata": {
            "artifact_id": artifact_id,
            "created_at": "2026-07-16T10:00:00+00:00",
            "executor_type": "market_backtest",
            "data_source": "historical",
        },
        "specification": {
            "hypothesis_description": (
                f"Hypothesis for {artifact_id}"
            ),
            "symbol": symbol,
            "timeframe": timeframe,
        },
        "cycle": {
            "evidence_strength_evaluation": (
                evidence_strength_evaluation
            ),
        },
        "lineage": {
            "parent_artifact_id": parent_artifact_id,
            "lineage_type": lineage_type,
        },
    }


def build_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "result-root": build_artifact(
            artifact_id="artifact-root",
            parent_artifact_id=None,
            symbol="BTCUSDT",
            timeframe="1h",
            confidence=0.4,
            lineage_type="root",
        ),
        "result-child": build_artifact(
            artifact_id="artifact-child",
            parent_artifact_id="artifact-root",
            symbol="BTCUSDT",
            timeframe="4h",
            confidence=0.8,
            lineage_type="hypothesis_refinement",
        ),
        "result-orphan": build_artifact(
            artifact_id="artifact-orphan",
            parent_artifact_id="missing-parent",
            symbol="ETHUSDT",
            timeframe="1h",
            confidence=None,
            lineage_type="feature_extension",
        ),
    }


def build_index() -> list[dict[str, Any]]:
    artifacts = build_artifacts()

    return build_artifact_index(
        result_ids=[
            "result-root",
            "result-child",
            "result-orphan",
        ],
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=artifacts,
        ),
    )


def test_build_dashboard_statistics_returns_counts():

    statistics = build_dashboard_statistics(
        artifacts=build_index(),
    )

    assert statistics["total"] == 3
    assert statistics["root_count"] == 1
    assert statistics["child_count"] == 2
    assert statistics["orphan_count"] == 1


def test_build_dashboard_statistics_returns_average_confidence():

    statistics = build_dashboard_statistics(
        artifacts=build_index(),
    )

    assert statistics["average_confidence"] == 0.6


def test_build_dashboard_statistics_returns_symbol_distribution():

    statistics = build_dashboard_statistics(
        artifacts=build_index(),
    )

    assert statistics["symbols"] == {
        "BTCUSDT": 2,
        "ETHUSDT": 1,
    }


def test_build_dashboard_statistics_returns_timeframe_distribution():

    statistics = build_dashboard_statistics(
        artifacts=build_index(),
    )

    assert statistics["timeframes"] == {
        "1h": 2,
        "4h": 1,
    }


def test_build_dashboard_statistics_handles_empty_artifacts():

    statistics = build_dashboard_statistics(
        artifacts=[],
    )

    assert statistics == {
        "total": 0,
        "root_count": 0,
        "child_count": 0,
        "orphan_count": 0,
        "average_confidence": None,
        "symbols": {},
        "timeframes": {},
    }


def test_build_dashboard_statistics_ignores_invalid_confidence():

    statistics = build_dashboard_statistics(
        artifacts=[
            {
                "artifact_id": "artifact-001",
                "parent_artifact_id": None,
                "parent_result_id": None,
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "confidence": "invalid",
            },
        ],
    )

    assert statistics["average_confidence"] is None


def test_web_index_renders_dashboard():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    response = app.test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert "Research dashboard" in body

    assert "Total artifacts" in body
    assert "<dd>3</dd>" in body

    assert "Root artifacts" in body
    assert "<dd>1</dd>" in body

    assert "Child artifacts" in body
    assert "<dd>2</dd>" in body

    assert "Orphan artifacts" in body

    assert "Average confidence" in body
    assert "0.6" in body

    assert "Artifacts by symbol" in body
    assert "BTCUSDT: 2" in body
    assert "ETHUSDT: 1" in body

    assert "Artifacts by timeframe" in body
    assert "1h: 2" in body
    assert "4h: 1" in body


def test_web_index_renders_empty_dashboard():

    app = create_app()

    response = app.test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert "Research dashboard" in body
    assert "Total artifacts" in body
    assert "Average confidence" in body
    assert "Not available" in body

    assert (
        "No symbol statistics are available."
        in body
    )

    assert (
        "No timeframe statistics are available."
        in body
    )