import json
import subprocess
import sys
from pathlib import Path

from src.storage import SqliteResearchCycleStore


def test_cli_package_runs_in_separate_process(
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

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "--database",
            str(db_path),
            "get-research-cycle",
            "result-001",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""

    parsed = json.loads(completed.stdout)

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