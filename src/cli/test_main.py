import json
from io import StringIO
from pathlib import Path

from src.cli import main
from src.storage import SqliteResearchCycleStore


def test_main_reads_research_cycle_from_sqlite_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    store.save(
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

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "get-research-cycle",
            "result-001",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    parsed = json.loads(stdout.getvalue())

    assert parsed["result"]["id"] == "result-001"
    assert parsed["result"]["success"] is True

    assert (
        parsed["evidence_strength_evaluation"]["level"]
        == "very_strong"
    )

    assert parsed["hypothesis_decision"]["is_supported"] is True

    assert (
        parsed["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )


def test_main_reports_missing_research_cycle(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "get-research-cycle",
            "unknown-result-id",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == "Research cycle not found: unknown-result-id\n"
    )