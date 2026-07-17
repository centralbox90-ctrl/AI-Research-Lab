from datetime import datetime, UTC

from src.application.artifact_history import (
    ArtifactHistoryEntry,
)
from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.artifact_metadata import (
    ArtifactMetadata,
)
from src.application.research_artifact import (
    ResearchArtifact,
)


def test_research_artifact_contains_metadata_lineage_history_and_comparisons():

    metadata = ArtifactMetadata(
        artifact_id="artifact-001",
        schema_version="1.0",
        created_at=datetime.now(UTC),
        experiment_id="experiment-001",
        executor_type="market_backtest_executor",
        executor_version="1.0",
        data_source="BTCUSDT_1H",
        code_version="abc123",
    )

    lineage = ArtifactLineage(
        parent_artifact_id="artifact-000",
        lineage_type="derived_from",
        change_description="Added ADX confirmation feature",
        created_from_experiment="experiment-001",
    )

    history = [
        ArtifactHistoryEntry(
            artifact_id="artifact-001",
            previous_artifact_id="artifact-000",
            event_type="created",
            description="Artifact created from experiment",
            created_at=datetime.now(UTC),
        )
    ]

    artifact = ResearchArtifact(
        metadata=metadata,
        lineage=lineage,
        history=history,
        comparisons=[],
        result={"profit": 25},
        evaluation={"confidence": 0.7},
        conclusion="positive result",
    )

    assert artifact.metadata.artifact_id == "artifact-001"

    assert (
        artifact.lineage.parent_artifact_id
        == "artifact-000"
    )

    assert (
        artifact.history[0].event_type
        == "created"
    )

    assert artifact.comparisons == []

    assert artifact.result["profit"] == 25

    assert artifact.evaluation["confidence"] == 0.7

    assert artifact.conclusion == "positive result"