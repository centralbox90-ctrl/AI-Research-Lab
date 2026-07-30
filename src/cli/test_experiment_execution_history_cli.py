from __future__ import annotations

import json
from io import StringIO

from src.cli.research_cli import ResearchCli


class StubResearchCycleCommand:
    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> None:
        return None


class StubExecutionHistoryCommand:
    def __init__(self) -> None:
        self.calls: list[
            tuple[str, int | None]
        ] = []

    def execute(
        self,
        execution_id: str,
        *,
        indent: int | None = 2,
    ) -> str:
        self.calls.append(
            (
                execution_id,
                indent,
            )
        )

        return json.dumps(
            {
                "schema_version": 1,
                "execution_id": execution_id,
                "snapshot_count": 3,
                "snapshots": [],
            },
            indent=indent,
        )


class MissingExecutionHistoryCommand:
    def execute(
        self,
        execution_id: str,
        *,
        indent: int | None = 2,
    ) -> None:
        return None


class FailingExecutionHistoryCommand:
    def execute(
        self,
        execution_id: str,
        *,
        indent: int | None = 2,
    ) -> str:
        raise ValueError(
            "invalid execution identity"
        )


def build_cli(
    command: object | None,
) -> ResearchCli:
    return ResearchCli(
        StubResearchCycleCommand(),
        get_experiment_execution_history_command=(
            command
        ),
    )


def test_research_cli_gets_execution_history(
) -> None:
    command = StubExecutionHistoryCommand()
    cli = build_cli(command)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-experiment-execution-history",
            "execution-rsi",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert command.calls == [
        (
            "execution-rsi",
            2,
        ),
    ]
    assert json.loads(stdout.getvalue())[
        "execution_id"
    ] == "execution-rsi"


def test_research_cli_supports_compact_execution_history(
) -> None:
    command = StubExecutionHistoryCommand()
    cli = build_cli(command)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-experiment-execution-history",
            "execution-rsi",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert command.calls == [
        (
            "execution-rsi",
            None,
        ),
    ]
    assert "\n" not in stdout.getvalue().rstrip(
        "\n"
    )


def test_research_cli_reports_missing_execution_history(
) -> None:
    cli = build_cli(
        MissingExecutionHistoryCommand()
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
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


def test_research_cli_reports_execution_history_error(
) -> None:
    cli = build_cli(
        FailingExecutionHistoryCommand()
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-experiment-execution-history",
            "execution-invalid",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == (
            "Unable to get experiment execution "
            "history: invalid execution identity\n"
        )
    )


def test_research_cli_reports_unconfigured_execution_history(
) -> None:
    cli = build_cli(None)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-experiment-execution-history",
            "execution-rsi",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == (
            "Get experiment execution history "
            "command is not configured.\n"
        )
    )
