import json
from pathlib import Path

from src.application import ListStoredResearchCycles
from src.cli import ListStoredResearchCyclesCommand
from src.storage import SqliteResearchCycleStore


def test_list_stored_research_cycles_command_returns_json_ids(
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
            },
        },
    )

    store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
            },
        },
    )

    command = ListStoredResearchCyclesCommand(
        list_stored_research_cycles=ListStoredResearchCycles(
            store=store,
        ),
    )

    rendered = command.execute()

    assert json.loads(rendered) == [
        "result-001",
        "result-002",
    ]


def test_list_stored_research_cycles_command_returns_empty_json_array(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    command = ListStoredResearchCyclesCommand(
        list_stored_research_cycles=ListStoredResearchCycles(
            store=store,
        ),
    )

    assert json.loads(command.execute()) == []


def test_list_stored_research_cycles_command_supports_compact_json(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
            },
        },
    )

    command = ListStoredResearchCyclesCommand(
        list_stored_research_cycles=ListStoredResearchCycles(
            store=store,
        ),
    )

    rendered = command.execute(
        indent=None,
    )

    assert rendered == '["result-001"]'
    assert "\n" not in rendered