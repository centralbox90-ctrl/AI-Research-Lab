import pytest

from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)


def test_artifact_comparison_factory_creation():

    factory = ArtifactComparisonFactory()

    comparison = factory.create(
        artifact_a_id="artifact-001",
        artifact_b_id="artifact-002",
        previous_hypothesis=(
            "Williams predicts reversal"
        ),
        current_hypothesis=(
            "Williams plus ADX predicts reversal"
        ),
        hypothesis_change_reason=(
            "Added trend confirmation"
        ),
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
        confidence_change_reason=(
            "Stronger validation evidence"
        ),
    )

    assert comparison.artifact_a_id == "artifact-001"
    assert comparison.artifact_b_id == "artifact-002"

    assert (
        comparison.hypothesis_evolution.previous_hypothesis
        == "Williams predicts reversal"
    )

    assert (
        comparison.hypothesis_evolution.current_hypothesis
        == "Williams plus ADX predicts reversal"
    )

    assert (
        comparison.evidence_evolution.previous_evidence
        == {
            "net_profit": -11.17,
            "win_rate": 35.71,
            "total_trades": 42,
        }
    )

    assert (
        comparison.evidence_evolution.current_evidence
        == {
            "net_profit": -8.64,
            "win_rate": 33.33,
            "total_trades": 42,
        }
    )

    metric_deltas = {
        delta.metric_name: delta
        for delta in (
            comparison.evidence_evolution.metric_deltas
        )
    }

    assert metric_deltas["net_profit"].direction == "increased"
    assert (
        metric_deltas["net_profit"].absolute_delta
        == pytest.approx(2.53)
    )

    assert metric_deltas["win_rate"].direction == "decreased"
    assert (
        metric_deltas["win_rate"].absolute_delta
        == pytest.approx(-2.38)
    )

    assert (
        metric_deltas["total_trades"].direction
        == "unchanged"
    )

    assert (
        comparison.evidence_evolution.change_reason
        == "Evidence changed between research artifacts."
    )

    assert (
        comparison.confidence_evolution.previous_confidence
        == 0.45
    )

    assert (
        comparison.confidence_evolution.current_confidence
        == 0.72
    )