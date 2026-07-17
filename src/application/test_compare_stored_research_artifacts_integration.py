from typing import Any

from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)


class FakeArtifactGetter:
    def __init__(
        self,
        artifacts: dict[str, dict[str, Any]],
    ) -> None:
        self.artifacts = artifacts

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any]:
        return self.artifacts[result_id]


def build_artifact(
    artifact_id: str,
    hypothesis_description: str,
    evidence: dict[str, Any],
    confidence: float,
) -> dict[str, Any]:
    return {
        "metadata": {
            "artifact_id": artifact_id,
        },
        "specification": {
            "hypothesis_title": "Test hypothesis",
            "hypothesis_description": (
                hypothesis_description
            ),
        },
        "cycle": {
            "evidence": {
                "data": evidence,
            },
            "evidence_strength_evaluation": {
                "score": confidence,
            },
        },
    }


def test_compare_stored_research_artifacts_with_real_extractor():

    getter = FakeArtifactGetter(
        artifacts={
            "result-001": build_artifact(
                artifact_id="artifact-001",
                hypothesis_description=(
                    "Williams predicts reversal"
                ),
                evidence={
                    "sample_size": 500,
                    "markets": 1,
                },
                confidence=0.45,
            ),
            "result-002": build_artifact(
                artifact_id="artifact-002",
                hypothesis_description=(
                    "Williams plus ADX predicts reversal"
                ),
                evidence={
                    "sample_size": 5000,
                    "markets": 5,
                },
                confidence=0.72,
            ),
        }
    )

    use_case = CompareStoredResearchArtifacts(
        artifact_getter=getter,
        input_extractor=(
            ArtifactComparisonInputExtractor()
        ),
    )

    comparison = use_case.execute(
        artifact_a_result_id="result-001",
        artifact_b_result_id="result-002",
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
        comparison.hypothesis_evolution.change_reason
        == "Hypothesis changed between research artifacts."
    )

    assert comparison.evidence_evolution.previous_evidence == {
        "sample_size": 500,
        "markets": 1,
    }

    assert comparison.evidence_evolution.current_evidence == {
        "sample_size": 5000,
        "markets": 5,
    }

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

    assert (
        comparison.confidence_evolution.change_reason
        == "Confidence increased."
    )