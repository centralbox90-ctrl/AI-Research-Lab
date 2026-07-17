from pathlib import Path

from src.application import GetStoredResearchCycle
from src.storage import SqliteResearchCycleStore


def test_get_stored_research_cycle_returns_persisted_payload(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    serialized_cycle = {
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
    }

    store.save(
        result_id="result-001",
        serialized_cycle=serialized_cycle,
    )

    use_case = GetStoredResearchCycle(
        store=store,
    )

    stored = use_case.execute("result-001")

    assert stored == serialized_cycle
    assert stored["result"]["id"] == "result-001"
    assert stored["hypothesis_decision"]["is_supported"] is True


def test_get_stored_research_cycle_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    use_case = GetStoredResearchCycle(
        store=store,
    )

    assert use_case.execute("unknown-result-id") is None


def test_get_stored_research_cycle_reads_data_from_new_store_instance(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    first_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    first_store.save(
        result_id="result-002",
        serialized_cycle={
            "result": {
                "id": "result-002",
                "success": True,
            },
        },
    )

    second_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    use_case = GetStoredResearchCycle(
        store=second_store,
    )

    stored = use_case.execute("result-002")

    assert stored is not None
    assert stored["result"]["id"] == "result-002"
    assert stored["result"]["success"] is True