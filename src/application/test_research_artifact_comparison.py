from datetime import UTC, datetime

from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.artifact_history import (
    ArtifactHistoryEntry,
)
from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.artifact_metadata import (
    ArtifactMetadata,
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
from src.application.research_artifact import (
    ResearchArtifact,
)


def test_research_artifact_contains_comparison():

    comparison = ArtifactComparison(
        artifact_a_id="artifact-001",
        artifact_b_id="artifact-002",
        hypothesis_evolution=HypothesisEvolution(
            previous_hypothesis="Old hypothesis",
            current_hypothesis="New hypothesis",
            change_reason="Hypothesis changed.",
        ),
        evidence_evolution=EvidenceEvolution(
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
        ),
        confidence_evolution=ConfidenceEvolution(
            previous_confidence=0.4,
            current_confidence=0.8,
            change_reason="Confidence increased.",
        ),
    )

    artifact = ResearchArtifact(
        metadata=ArtifactMetadata(
            artifact_id="artifact-002",
            schema_version="1.0",
            created_at=datetime.now(UTC),
            experiment_id="experiment-002",
            executor_type="executor",
            executor_version="1.0",
            data_source="BTCUSDT",
            code_version="abc123",
        ),
        lineage=ArtifactLineage(
            parent_artifact_id="artifact-001",
            lineage_type="derived_from",
            change_description="Changed hypothesis",
            created_from_experiment="experiment-002",
        ),
        history=[
            ArtifactHistoryEntry(
                artifact_id="artifact-002",
                previous_artifact_id="artifact-001",
                event_type="comparison_added",
                description="Added comparison",
                created_at=datetime.now(UTC),
            )
        ],
        comparisons=[
            comparison
        ],
        result={},
        evaluation={},
        conclusion="Updated artifact",
    )

    assert len(artifact.comparisons) == 1

    assert (
        artifact.comparisons[0]
        .evidence_evolution
        .current_evidence
        == {
            "sample_size": 5000,
            "markets": 5,
        }
    )

    assert (
        artifact.comparisons[0]
        .evidence_evolution
        .change_reason
        == "Evidence changed between research artifacts."
    )

    assert (
        artifact.comparisons[0]
        .confidence_evolution
        .current_confidence
        == 0.8
    )