from pathlib import Path

from src.storage import SqliteResearchCycleStore


def test_sqlite_research_cycle_store_saves_and_loads_payload(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    serialized_cycle = {
        "result": {
            "id": "result-001",
            "success": True,
        },
        "evidence_strength_evaluation": {
            "level": "very_strong",
            "score": 1.0,
        },
        "hypothesis_decision": {
            "is_supported": True,
        },
        "next_experiment_selection": {
            "action": "replicate_experiment",
        },
    }

    store.save(
        result_id="result-001",
        serialized_cycle=serialized_cycle,
    )

    loaded_cycle = store.get("result-001")

    assert loaded_cycle == serialized_cycle
    assert loaded_cycle["result"]["id"] == "result-001"
    assert loaded_cycle["hypothesis_decision"]["is_supported"] is True


def test_sqlite_research_cycle_store_updates_existing_payload(
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
                "success": False,
            },
        },
    )

    store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
                "success": True,
            },
        },
    )

    loaded_cycle = store.get("result-001")

    assert loaded_cycle is not None
    assert loaded_cycle["result"]["success"] is True


def test_sqlite_research_cycle_store_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    assert store.get("unknown-result-id") is None


def test_sqlite_research_cycle_store_lists_result_ids(
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

    assert store.list_result_ids() == [
        "result-001",
        "result-002",
    ]


def test_sqlite_research_cycle_store_lists_no_ids_when_empty(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    assert store.list_result_ids() == []