import json
from pathlib import Path

from src.application import (
    GetStoredResearchArtifact,
)
from src.cli import (
    GetStoredResearchArtifactCommand,
)
from src.storage import (
    SqliteResearchCycleStore,
)


def build_artifact() -> dict:
    return {
        "artifact_version": 1,
        "result": {
            "id": "artifact-test-id",
            "success": True,
        },
    }


def test_get_stored_research_artifact_command_returns_json(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    store.save(
        result_id="artifact-test-id",
        serialized_cycle=build_artifact(),
    )

    command = GetStoredResearchArtifactCommand(
        get_stored_research_artifact=(
            GetStoredResearchArtifact(
                store=store,
            )
        ),
    )

    rendered = command.execute(
        "artifact-test-id",
    )

    assert rendered is not None

    parsed = json.loads(
        rendered,
    )

    assert parsed["artifact_version"] == 1
    assert parsed["result"]["id"] == "artifact-test-id"


def test_get_stored_research_artifact_command_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    command = GetStoredResearchArtifactCommand(
        get_stored_research_artifact=(
            GetStoredResearchArtifact(
                store=store,
            )
        ),
    )

    rendered = command.execute(
        "missing-id",
    )

    assert rendered is None