from pathlib import Path

from src.application import ListStoredResearchCycles
from src.storage import SqliteResearchCycleStore


def test_list_stored_research_cycles_returns_persisted_result_ids(
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

    use_case = ListStoredResearchCycles(
        store=store,
    )

    assert use_case.execute() == [
        "result-001",
        "result-002",
    ]


def test_list_stored_research_cycles_returns_empty_list(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    use_case = ListStoredResearchCycles(
        store=store,
    )

    assert use_case.execute() == []