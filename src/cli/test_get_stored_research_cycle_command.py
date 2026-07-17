import json
from pathlib import Path

from src.application import GetStoredResearchCycle
from src.cli import GetStoredResearchCycleCommand
from src.storage import SqliteResearchCycleStore


def test_get_stored_research_cycle_command_returns_persisted_json(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    first_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    first_store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
                "success": True,
            },
            "evidence_strength_evaluation": {
                "level": "very_strong",
            },
            "hypothesis_decision": {
                "is_supported": True,
            },
            "next_experiment_selection": {
                "action": "replicate_experiment",
            },
        },
    )

    second_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=GetStoredResearchCycle(
            store=second_store,
        ),
    )

    rendered = command.execute("result-001")

    assert rendered is not None

    parsed = json.loads(rendered)

    assert parsed["result"]["id"] == "result-001"
    assert parsed["result"]["success"] is True
    assert parsed["hypothesis_decision"]["is_supported"] is True

    assert (
        parsed["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )


def test_get_stored_research_cycle_command_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=GetStoredResearchCycle(
            store=store,
        ),
    )

    assert command.execute("unknown-result-id") is None


def test_get_stored_research_cycle_command_supports_compact_json(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    store.save(
        result_id="result-002",
        serialized_cycle={
            "result": {
                "id": "result-002",
                "success": True,
            },
        },
    )

    command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=GetStoredResearchCycle(
            store=store,
        ),
    )

    rendered = command.execute(
        "result-002",
        indent=None,
    )

    assert rendered is not None
    assert "\n" not in rendered
    assert json.loads(rendered)["result"]["id"] == "result-002"