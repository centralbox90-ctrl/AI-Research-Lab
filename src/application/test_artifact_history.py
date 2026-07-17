from datetime import datetime, UTC

from src.application.artifact_history import (
    ArtifactHistoryEntry,
)


def test_artifact_history_entry_creation():

    history = ArtifactHistoryEntry(
        artifact_id="artifact-002",
        previous_artifact_id="artifact-001",
        event_type="experiment_changed",
        description="Added ADX confirmation feature",
        created_at=datetime.now(UTC),
    )

    assert history.artifact_id == "artifact-002"

    assert (
        history.previous_artifact_id
        == "artifact-001"
    )

    assert (
        history.event_type
        == "experiment_changed"
    )

    assert (
        history.description
        == "Added ADX confirmation feature"
    )