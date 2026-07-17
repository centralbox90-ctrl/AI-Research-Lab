import json
from io import StringIO
from pathlib import Path

from src.application import (
    GetStoredResearchCycle,
    ListStoredResearchCycles,
)
from src.cli import (
    GetStoredResearchCycleCommand,
    ListStoredResearchCyclesCommand,
    ResearchCli,
)
from src.storage import SqliteResearchCycleStore


def test_research_cli_lists_persisted_cycle_ids(
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

    cli = ResearchCli(
        get_research_cycle_command=GetStoredResearchCycleCommand(
            get_stored_research_cycle=GetStoredResearchCycle(
                store=store,
            ),
        ),
        list_research_cycles_command=ListStoredResearchCyclesCommand(
            list_stored_research_cycles=ListStoredResearchCycles(
                store=store,
            ),
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "list-research-cycles",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    assert json.loads(stdout.getvalue()) == [
        "result-001",
        "result-002",
    ]


def test_research_cli_lists_cycles_as_compact_json(
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

    cli = ResearchCli(
        get_research_cycle_command=GetStoredResearchCycleCommand(
            get_stored_research_cycle=GetStoredResearchCycle(
                store=store,
            ),
        ),
        list_research_cycles_command=ListStoredResearchCyclesCommand(
            list_stored_research_cycles=ListStoredResearchCycles(
                store=store,
            ),
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "list-research-cycles",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue() == '["result-001"]\n'