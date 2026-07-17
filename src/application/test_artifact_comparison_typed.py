from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.confidence_evolution import (
    ConfidenceEvolution,
)
from src.application.evidence_evolution import (
    EvidenceEvolution,
)
from src.application.hypothesis_evolution import (
    HypothesisEvolution,
)


def test_artifact_comparison_uses_evolution_models():

    hypothesis = HypothesisEvolution(
        previous_hypothesis=(
            "Williams predicts reversal"
        ),
        current_hypothesis=(
            "Williams plus ADX predicts reversal"
        ),
        change_reason=(
            "Added trend confirmation"
        ),
    )

    evidence = EvidenceEvolution(
        previous_evidence={
            "sample_size": 500,
            "markets": 1,
        },
        current_evidence={
            "sample_size": 5000,
            "markets": 5,
        },
        change_reason=(
            "Evidence changed between research artifacts."
        ),
    )

    confidence = ConfidenceEvolution(
        previous_confidence=0.45,
        current_confidence=0.72,
        change_reason=(
            "More validation evidence"
        ),
    )

    comparison = ArtifactComparison(
        artifact_a_id="artifact-001",
        artifact_b_id="artifact-002",
        hypothesis_evolution=hypothesis,
        evidence_evolution=evidence,
        confidence_evolution=confidence,
    )

    assert (
        comparison.hypothesis_evolution.current_hypothesis
        == "Williams plus ADX predicts reversal"
    )

    assert (
        comparison.evidence_evolution.previous_evidence
        == {
            "sample_size": 500,
            "markets": 1,
        }
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
        == "Evidence changed between research artifacts."
    )

    assert (
        comparison.confidence_evolution.current_confidence
        == 0.72
    )