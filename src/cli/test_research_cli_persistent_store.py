import json
from io import StringIO
from pathlib import Path

from src.application import GetStoredResearchCycle
from src.cli import GetStoredResearchCycleCommand, ResearchCli
from src.storage import SqliteResearchCycleStore


def test_research_cli_reads_cycle_from_persistent_sqlite_store(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    writer_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    writer_store.save(
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

    reader_store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=GetStoredResearchCycle(
            store=reader_store,
        ),
    )

    cli = ResearchCli(
        get_research_cycle_command=command,
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
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