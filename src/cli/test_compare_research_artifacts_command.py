import json

import pytest

from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)
from src.cli.compare_research_artifacts_command import (
    CompareResearchArtifactsCommand,
)


class FakeCompareStoredResearchArtifacts:
    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ):
        assert artifact_a_result_id == "result-001"
        assert artifact_b_result_id == "result-002"

        factory = ArtifactComparisonFactory()

        return factory.create(
            artifact_a_id="artifact-001",
            artifact_b_id="artifact-002",
            previous_hypothesis=(
                "Williams predicts reversal"
            ),
            current_hypothesis=(
                "Williams plus ADX predicts reversal"
            ),
            hypothesis_change_reason=(
                "Hypothesis became more specific"
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
                "Confidence increased."
            ),
        )


def test_compare_research_artifacts_command_returns_json():

    command = CompareResearchArtifactsCommand(
        compare_stored_research_artifacts=(
            FakeCompareStoredResearchArtifacts()
        ),
    )

    rendered = command.execute(
        artifact_a_result_id="result-001",
        artifact_b_result_id="result-002",
        indent=2,
    )

    payload = json.loads(rendered)

    assert payload["artifact_a_id"] == "artifact-001"
    assert payload["artifact_b_id"] == "artifact-002"

    assert (
        payload["hypothesis_evolution"][
            "current_hypothesis"
        ]
        == "Williams plus ADX predicts reversal"
    )

    evidence_evolution = payload["evidence_evolution"]

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
        payload["confidence_evolution"][
            "current_confidence"
        ]
        == 0.72
    )