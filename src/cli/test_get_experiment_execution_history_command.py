from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from src.application.get_experiment_execution_history import (
    GetExperimentExecutionHistory,
)
from src.cli.get_experiment_execution_history_command import (
    GetExperimentExecutionHistoryCommand,
)
from src.research.experiment_execution import (
    ExperimentExecution,
)


class StubExecutionHistoryReader:
    def __init__(
        self,
        snapshots: tuple[
            ExperimentExecution,
            ...,
        ],
    ) -> None:
        self.snapshots = snapshots
        self.calls: list[str] = []

    def history(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        self.calls.append(execution_id)

        return self.snapshots


def build_history(
) -> tuple[ExperimentExecution, ...]:
    pending = ExperimentExecution(
        execution_id="execution-rsi",
        experiment_id="experiment-rsi",
        specification_fingerprint="a" * 64,
        correlation_id="lifecycle-42",
        created_at=datetime(
            2026,
            7,
            29,
            13,
            0,
            tzinfo=UTC,
        ),
    )
    running = pending.start(
        environment_fingerprint="b" * 64,
        started_at=datetime(
            2026,
            7,
            29,
            13,
            1,
            tzinfo=UTC,
        ),
    )
    succeeded = running.succeed(
        result_id="result-rsi",
        finished_at=datetime(
            2026,
            7,
            29,
            13,
            2,
            tzinfo=UTC,
        ),
    )

    return (
        pending,
        running,
        succeeded,
    )


def build_command(
    snapshots: tuple[
        ExperimentExecution,
        ...,
    ],
) -> tuple[
    GetExperimentExecutionHistoryCommand,
    StubExecutionHistoryReader,
]:
    reader = StubExecutionHistoryReader(
        snapshots
    )
    application = GetExperimentExecutionHistory(
        reader=reader
    )

    return (
        GetExperimentExecutionHistoryCommand(
            application=application
        ),
        reader,
    )


def test_renders_execution_history(
) -> None:
    command, reader = build_command(
        build_history()
    )

    rendered = command.execute(
        "  execution-rsi  "
    )
    payload = json.loads(rendered)

    assert reader.calls == ["execution-rsi"]
    assert payload["schema_version"] == 1
    assert payload["execution_id"] == (
        "execution-rsi"
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
    assert payload["snapshots"][2][
        "result_id"
    ] == "result-rsi"


def test_supports_compact_json(
) -> None:
    command, _ = build_command(
        build_history()
    )

    rendered = command.execute(
        "execution-rsi",
        indent=None,
    )

    assert rendered is not None
    assert "\n" not in rendered
    assert json.loads(rendered)[
        "snapshot_count"
    ] == 3


def test_returns_none_when_history_is_missing(
) -> None:
    command, reader = build_command(())

    assert command.execute(
        "execution-missing"
    ) is None
    assert reader.calls == [
        "execution-missing",
    ]


def test_rejects_invalid_application(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "application must be a "
            "GetExperimentExecutionHistory"
        ),
    ):
        GetExperimentExecutionHistoryCommand(
            application=object()
        )
