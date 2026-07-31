from pathlib import Path

import pytest

from src.application import ListStoredResearchCycles
from src.application.get_stored_research_artifact import (
    StoredResearchArtifactIntegrityError,
)
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


def test_list_stored_research_cycles_fails_closed_on_identity_mismatch(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research_cycles.db"
    )
    first_store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    first_store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
            },
        },
    )
    first_store.save(
        result_id="result-002",
        serialized_cycle={
            "result": {
                "id": "result-corrupt",
            },
        },
    )

    reopened_store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    use_case = ListStoredResearchCycles(
        store=reopened_store,
    )

    with pytest.raises(
        StoredResearchArtifactIntegrityError,
        match=(
            "legacy research cycle result id does "
            "not match storage key"
        ),
    ) as error:
        use_case.execute()

    assert error.value.result_id == "result-002"
