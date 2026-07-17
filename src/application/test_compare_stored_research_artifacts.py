from typing import Any

from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)


class FakeArtifactGetter:
    def __init__(
        self,
        artifacts: dict[str, dict[str, Any]],
    ) -> None:
        self.artifacts = artifacts
        self.requested_result_ids: list[str] = []

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any]:
        self.requested_result_ids.append(result_id)
        return self.artifacts[result_id]


class FakeComparisonInputExtractor:
    def extract(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "artifact_a_id": artifact_a["metadata"][
                "artifact_id"
            ],
            "artifact_b_id": artifact_b["metadata"][
                "artifact_id"
            ],
            "previous_hypothesis": artifact_a[
                "hypothesis"
            ],
            "current_hypothesis": artifact_b[
                "hypothesis"
            ],
            "hypothesis_change_reason": (
                "Hypothesis became more specific"
            ),
            "previous_evidence": artifact_a[
                "evidence"
            ],
            "current_evidence": artifact_b[
                "evidence"
            ],
            "evidence_change_reason": (
                "Evidence changed between artifacts"
            ),
            "previous_confidence": artifact_a[
                "confidence"
            ],
            "current_confidence": artifact_b[
                "confidence"
            ],
            "confidence_change_reason": (
                "Evidence became stronger"
            ),
        }


def test_compare_stored_research_artifacts():

    getter = FakeArtifactGetter(
        artifacts={
            "result-001": {
                "metadata": {
                    "artifact_id": "artifact-001",
                },
                "hypothesis": (
                    "Williams predicts reversal"
                ),
                "evidence": {
                    "sample_size": 500,
                    "markets": 1,
                },
                "confidence": 0.45,
            },
            "result-002": {
                "metadata": {
                    "artifact_id": "artifact-002",
                },
                "hypothesis": (
                    "Williams plus ADX predicts reversal"
                ),
                "evidence": {
                    "sample_size": 5000,
                    "markets": 5,
                },
                "confidence": 0.72,
            },
        }
    )

    use_case = CompareStoredResearchArtifacts(
        artifact_getter=getter,
        input_extractor=FakeComparisonInputExtractor(),
    )

    comparison = use_case.execute(
        artifact_a_result_id="result-001",
        artifact_b_result_id="result-002",
    )

    assert getter.requested_result_ids == [
        "result-001",
        "result-002",
    ]

    assert comparison.artifact_a_id == "artifact-001"
    assert comparison.artifact_b_id == "artifact-002"

    assert (
        comparison.hypothesis_evolution.current_hypothesis
        == "Williams plus ADX predicts reversal"
    )

    assert (
        comparison.evidence_evolution.current_evidence
        == {
            "sample_size": 5000,
            "markets": 5,
        }
    )

    assert (
        comparison.evidence_evolution.change_reason
        == "Evidence changed between artifacts"
    )

    assert (
        comparison.confidence_evolution.current_confidence
        == 0.72
    )