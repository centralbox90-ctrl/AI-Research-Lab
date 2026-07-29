from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.get_experiment_execution_history import (
    GetExperimentExecutionHistory,
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


class InvalidSequenceReader:
    def history(
        self,
        execution_id: str,
    ) -> list[object]:
        return []


class InvalidSnapshotReader:
    def history(
        self,
        execution_id: str,
    ) -> tuple[object, ...]:
        return (object(),)


def build_history(
    *,
    execution_id: str = "execution-1",
) -> tuple[ExperimentExecution, ...]:
    pending = ExperimentExecution(
        execution_id=execution_id,
        experiment_id="experiment-rsi",
        specification_fingerprint=(
            "a" * 64
        ),
        correlation_id="lifecycle-42",
        created_at=datetime(
            2026,
            7,
            29,
            10,
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
            10,
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
            10,
            2,
            tzinfo=UTC,
        ),
    )

    return (
        pending,
        running,
        succeeded,
    )


def test_returns_execution_history(
) -> None:
    snapshots = build_history()
    reader = StubExecutionHistoryReader(
        snapshots
    )
    use_case = GetExperimentExecutionHistory(
        reader=reader
    )

    result = use_case.execute(
        "  execution-1  "
    )

    assert result == snapshots
    assert reader.calls == ["execution-1"]
    assert [
        snapshot.status.value
        for snapshot in result
    ] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
    ]


def test_returns_empty_history_when_missing(
) -> None:
    reader = StubExecutionHistoryReader(())
    use_case = GetExperimentExecutionHistory(
        reader=reader
    )

    assert use_case.execute(
        "execution-missing"
    ) == ()
    assert reader.calls == [
        "execution-missing",
    ]


def test_rejects_reader_without_history(
) -> None:
    with pytest.raises(
        TypeError,
        match="reader must provide history",
    ):
        GetExperimentExecutionHistory(
            reader=object()
        )


@pytest.mark.parametrize(
    "execution_id, error_type, message",
    [
        (
            None,
            TypeError,
            "execution_id must be a string",
        ),
        (
            "   ",
            ValueError,
            "execution_id must not be empty",
        ),
    ],
)
def test_rejects_invalid_execution_id(
    execution_id: object,
    error_type: type[Exception],
    message: str,
) -> None:
    use_case = GetExperimentExecutionHistory(
        reader=StubExecutionHistoryReader(
            ()
        )
    )

    with pytest.raises(
        error_type,
        match=message,
    ):
        use_case.execute(execution_id)


def test_rejects_non_tuple_history(
) -> None:
    use_case = GetExperimentExecutionHistory(
        reader=InvalidSequenceReader()
    )

    with pytest.raises(
        TypeError,
        match=(
            "execution history must be a tuple"
        ),
    ):
        use_case.execute("execution-1")


def test_rejects_non_execution_snapshot(
) -> None:
    use_case = GetExperimentExecutionHistory(
        reader=InvalidSnapshotReader()
    )

    with pytest.raises(
        TypeError,
        match=(
            "execution history must contain "
            "ExperimentExecution values"
        ),
    ):
        use_case.execute("execution-1")


def test_rejects_snapshot_from_other_execution(
) -> None:
    reader = StubExecutionHistoryReader(
        build_history(
            execution_id="execution-other"
        )
    )
    use_case = GetExperimentExecutionHistory(
        reader=reader
    )

    with pytest.raises(
        ValueError,
        match=(
            "execution history contains a "
            "different execution_id"
        ),
    ):
        use_case.execute("execution-1")
