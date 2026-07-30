from __future__ import annotations

import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.cli.get_experiment_execution_history_command import (
    GetExperimentExecutionHistoryCommand,
)
from src.cli.main import (
    build_research_cli,
    main,
)
from src.research.experiment_execution import (
    ExperimentExecution,
)
from src.storage import (
    SqliteExperimentExecutionRecorder,
)


def build_history(
) -> tuple[ExperimentExecution, ...]:
    pending = ExperimentExecution(
        execution_id="execution-production-rsi",
        experiment_id="experiment-rsi",
        specification_fingerprint="a" * 64,
        correlation_id="production-lifecycle-42",
        created_at=datetime(
            2026,
            7,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )
    running = pending.start(
        environment_fingerprint="b" * 64,
        started_at=datetime(
            2026,
            7,
            30,
            10,
            1,
            tzinfo=timezone.utc,
        ),
    )
    succeeded = running.succeed(
        result_id="result-production-rsi",
        finished_at=datetime(
            2026,
            7,
            30,
            10,
            2,
            tzinfo=timezone.utc,
        ),
    )

    return (
        pending,
        running,
        succeeded,
    )


def test_build_research_cli_configures_execution_history(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    cli = build_research_cli(
        db_path=database_path
    )
    command = (
        cli
        .get_experiment_execution_history_command
    )

    assert isinstance(
        command,
        GetExperimentExecutionHistoryCommand,
    )
    assert isinstance(
        command._application._reader,
        SqliteExperimentExecutionRecorder,
    )
    assert (
        command._application._reader.db_path
        == database_path
    )


def test_main_reads_execution_history_from_sqlite(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    recorder = (
        SqliteExperimentExecutionRecorder(
            db_path=database_path
        )
    )

    for snapshot in build_history():
        recorder.record(snapshot)

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            "get-experiment-execution-history",
            "execution-production-rsi",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(
        stdout.getvalue()
    )

    assert payload["schema_version"] == 1
    assert payload["execution_id"] == (
        "execution-production-rsi"
    )
    assert payload["snapshot_count"] == 3
    assert [
        snapshot["status"]
        for snapshot in payload["snapshots"]
    ] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
    ]
    assert all(
        snapshot["correlation_id"]
        == "production-lifecycle-42"
        for snapshot in payload["snapshots"]
    )
    assert payload["snapshots"][2][
        "result_id"
    ] == "result-production-rsi"


def test_main_reports_missing_execution_history(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            "get-experiment-execution-history",
            "execution-missing",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == (
            "Experiment execution history not found: "
            "execution-missing\n"
        )
    )
