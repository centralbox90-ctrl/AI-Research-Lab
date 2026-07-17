from src.application.artifact_comparison import (
    ArtifactComparison,
)


def test_artifact_comparison_creation():

    comparison = ArtifactComparison(
        artifact_a_id="artifact-001",
        artifact_b_id="artifact-002",
        hypothesis_evolution={
            "changed": True,
            "description": (
                "Added ADX confirmation"
            ),
        },
        evidence_evolution={
            "samples_increased": True,
            "description": (
                "Validated on more market periods"
            ),
        },
        confidence_evolution={
            "previous": 0.45,
            "current": 0.72,
        },
    )

    assert comparison.artifact_a_id == "artifact-001"

    assert comparison.artifact_b_id == "artifact-002"

    assert (
        comparison.hypothesis_evolution["changed"]
        is True
    )

    assert (
        comparison.evidence_evolution[
            "samples_increased"
        ]
        is True
    )

    assert (
        comparison.confidence_evolution["current"]
        == 0.72
    )