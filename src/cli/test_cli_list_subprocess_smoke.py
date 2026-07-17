import json
import subprocess
import sys
from pathlib import Path

from src.storage import SqliteResearchCycleStore


def test_cli_lists_research_cycles_in_separate_process(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    store = SqliteResearchCycleStore(
        db_path=db_path,
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

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "--database",
            str(db_path),
            "list-research-cycles",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""

    assert json.loads(completed.stdout) == [
        "result-001",
        "result-002",
    ]


def test_cli_lists_research_cycles_as_compact_json_in_separate_process(
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
            },
        },
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "--database",
            str(db_path),
            "list-research-cycles",
            "--compact",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert completed.stdout == '["result-001"]\n'