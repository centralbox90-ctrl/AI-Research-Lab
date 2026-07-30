from __future__ import annotations

import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.cli.get_experiment_execution_history_command import (
    GetExperimentExecutionHistoryCommand,
)
from src.cli.list_experiment_executions_command import (
    ListExperimentExecutionsCommand,
)
from src.cli.main import build_research_cli, main
from src.cli.research_cli import ResearchCli
from src.research.experiment_execution import (
    ExperimentExecution,
)
from src.storage import (
    SqliteExperimentExecutionRecorder,
)


class StubResearchCycleCommand:
    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> None:
        return None


class StubListExperimentExecutionsCommand:
    def __init__(self) -> None:
        self.calls: list[int | None] = []

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        self.calls.append(indent)

        return json.dumps(
            {
                "schema_version": 1,
                "execution_count": 2,
                "execution_ids": [
                    "execution-a",
                    "execution-b",
                ],
            },
            indent=indent,
        )


class FailingListExperimentExecutionsCommand:
    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        raise ValueError(
            "catalog is unavailable"
        )


def build_cli(
    command: object | None,
) -> ResearchCli:
    return ResearchCli(
        StubResearchCycleCommand(),
        list_experiment_executions_command=command,
    )


def test_research_cli_lists_experiment_executions(
) -> None:
    command = StubListExperimentExecutionsCommand()
    cli = build_cli(command)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        ["list-experiment-executions"],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert command.calls == [2]
    assert json.loads(stdout.getvalue())[
        "execution_ids"
    ] == [
        "execution-a",
        "execution-b",
    ]


def test_research_cli_supports_compact_execution_listing(
) -> None:
    command = StubListExperimentExecutionsCommand()
    cli = build_cli(command)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "list-experiment-executions",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert command.calls == [None]
    assert "\n" not in stdout.getvalue().rstrip(
        "\n"
    )


def test_research_cli_reports_execution_listing_error(
) -> None:
    cli = build_cli(
        FailingListExperimentExecutionsCommand()
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        ["list-experiment-executions"],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "Unable to list experiment executions: "
        "catalog is unavailable\n"
    )


def test_research_cli_reports_unconfigured_execution_listing(
) -> None:
    cli = build_cli(None)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        ["list-experiment-executions"],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "List experiment executions command "
        "is not configured.\n"
    )


def build_execution(
    execution_id: str,
) -> ExperimentExecution:
    return ExperimentExecution(
        execution_id=execution_id,
        experiment_id="experiment-rsi",
        specification_fingerprint="a" * 64,
        correlation_id="research-lifecycle-42",
        created_at=datetime(
            2026,
            7,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_build_research_cli_configures_execution_listing(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    cli = build_research_cli(
        db_path=database_path
    )
    listing_command = (
        cli.list_experiment_executions_command
    )
    history_command = (
        cli.get_experiment_execution_history_command
    )

    assert isinstance(
        listing_command,
        ListExperimentExecutionsCommand,
    )
    assert isinstance(
        history_command,
        GetExperimentExecutionHistoryCommand,
    )
    assert (
        listing_command._application._catalog
        is history_command._application._reader
    )
    assert isinstance(
        listing_command._application._catalog,
        SqliteExperimentExecutionRecorder,
    )
    assert (
        listing_command._application._catalog.db_path
        == database_path
    )


def test_main_lists_experiment_executions_from_sqlite(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    recorder = SqliteExperimentExecutionRecorder(
        db_path=database_path
    )
    recorder.record(
        build_execution("execution-b")
    )
    recorder.record(
        build_execution("execution-a")
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            "list-experiment-executions",
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

    assert payload == {
        "schema_version": 1,
        "execution_count": 2,
        "execution_ids": [
            "execution-a",
            "execution-b",
        ],
    }


def test_main_lists_empty_experiment_execution_catalog(
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
            "list-experiment-executions",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert json.loads(stdout.getvalue()) == {
        "schema_version": 1,
        "execution_count": 0,
        "execution_ids": [],
    }
