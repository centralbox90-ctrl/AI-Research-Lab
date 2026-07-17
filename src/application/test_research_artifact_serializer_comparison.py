from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pytest

from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)


@dataclass
class FakeCycle:
    result: dict[str, Any]

    def __init__(self):
        self.result = {
            "id": "result-id",
        }


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Test question",
        question_description="Test description",
        hypothesis_title="Test hypothesis",
        hypothesis_description="Test hypothesis description",
        expected_result="Positive result",
        experiment_title="Test experiment",
        experiment_description="Test experiment description",
        data_source="generated",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="entry",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
        strategy_parameters={},
        tags=(),
    )


def build_comparison():
    factory = ArtifactComparisonFactory()

    return factory.create(
        artifact_a_id="artifact-001",
        artifact_b_id="artifact-002",
        previous_hypothesis="Old hypothesis",
        current_hypothesis="New hypothesis",
        hypothesis_change_reason="Hypothesis changed.",
        previous_evidence={
            "net_profit": -11.17,
            "win_rate": 35.71,
            "total_trades": 42,
        },
        current_evidence={
            "net_profit": -8.64,
            "win_rate": 33.33,
            "total_trades": 42,
        },
        evidence_change_reason=(
            "Evidence changed between research artifacts."
        ),
        previous_confidence=0.45,
        current_confidence=0.72,
        confidence_change_reason="Confidence increased.",
    )


def test_research_artifact_serializer_serializes_comparisons():

    serializer = ResearchArtifactSerializer()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=FakeCycle(),
        comparisons=[
            build_comparison(),
        ],
    )

    assert len(artifact["comparisons"]) == 1

    comparison = artifact["comparisons"][0]

    assert comparison["artifact_a_id"] == "artifact-001"
    assert comparison["artifact_b_id"] == "artifact-002"

    evidence_evolution = comparison["evidence_evolution"]

    assert evidence_evolution["current_evidence"] == {
        "net_profit": -8.64,
        "total_trades": 42,
        "win_rate": 33.33,
    }

    metric_deltas = {
        delta["metric_name"]: delta
        for delta in evidence_evolution["metric_deltas"]
    }

    assert metric_deltas["net_profit"]["direction"] == "increased"
    assert metric_deltas["net_profit"][
        "absolute_delta"
    ] == pytest.approx(2.53)

    assert metric_deltas["win_rate"]["direction"] == "decreased"
    assert metric_deltas["win_rate"][
        "absolute_delta"
    ] == pytest.approx(-2.38)

    assert (
        metric_deltas["total_trades"]["direction"]
        == "unchanged"
    )

    assert (
        evidence_evolution["change_reason"]
        == "Evidence changed between research artifacts."
    )

    assert "improvement_reason" not in evidence_evolution

    assert (
        comparison["confidence_evolution"][
            "current_confidence"
        ]
        == 0.72
    )