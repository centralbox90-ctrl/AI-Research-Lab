import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
)
from src.storage import (
    SqliteExperimentExecutionRecorder as ExportedRecorder,
)
from src.storage.sqlite_experiment_execution_recorder import (
    SqliteExperimentExecutionRecorder,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    12,
    0,
    tzinfo=timezone.utc,
)
SPECIFICATION_FINGERPRINT = "a" * 64
ENVIRONMENT_FINGERPRINT = "b" * 64


def build_pending(
    execution_id: str = "execution-1",
) -> ExperimentExecution:
    return ExperimentExecution(
        execution_id=execution_id,
        experiment_id=f"{execution_id}-experiment",
        specification_fingerprint=(
            SPECIFICATION_FINGERPRINT
        ),
        correlation_id="research-cycle-1",
        created_at=CREATED_AT,
    )


def build_running(
    execution_id: str = "execution-1",
) -> ExperimentExecution:
    return build_pending(
        execution_id
    ).start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=(
            CREATED_AT
            + timedelta(seconds=1)
        ),
    )


def build_succeeded(
    execution_id: str = "execution-1",
) -> ExperimentExecution:
    return build_running(
        execution_id
    ).succeed(
        result_id=f"{execution_id}-result",
        finished_at=(
            CREATED_AT
            + timedelta(seconds=2)
        ),
    )


def test_creates_parent_directory(
    tmp_path: Path,
) -> None:
    db_path = (
        tmp_path
        / "nested"
        / "executions.db"
    )

    SqliteExperimentExecutionRecorder(
        db_path
    )

    assert db_path.is_file()


def test_rejects_non_execution(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    with pytest.raises(
        TypeError,
        match=(
            "execution must be an "
            "ExperimentExecution"
        ),
    ):
        recorder.record(object())


def test_records_append_only_history(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()
    running = build_running()
    succeeded = build_succeeded()

    recorder.record(pending)
    recorder.record(running)
    recorder.record(succeeded)

    assert recorder.history(
        " execution-1 "
    ) == (
        pending,
        running,
        succeeded,
    )
    assert recorder.get_latest(
        "execution-1"
    ) == succeeded


def test_persists_across_instances(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    execution = build_succeeded()
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    recorder.record(execution)

    reopened = SqliteExperimentExecutionRecorder(
        db_path
    )

    assert reopened.get_latest(
        execution.execution_id
    ) == execution


def test_round_trips_failure(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    failed = build_running().fail(
        failure=ExperimentExecutionFailure(
            stage=(
                ExperimentExecutionFailureStage.EXECUTION
            ),
            error_type="RuntimeError",
            message="Executor failed.",
        ),
        finished_at=(
            CREATED_AT
            + timedelta(seconds=2)
        ),
    )

    recorder.record(failed)

    assert recorder.get_latest(
        failed.execution_id
    ) == failed


def test_isolates_execution_histories(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    first = build_pending("execution-1")
    second = build_pending("execution-2")

    recorder.record(second)
    recorder.record(first)

    assert recorder.history(
        first.execution_id
    ) == (first,)
    assert recorder.history(
        second.execution_id
    ) == (second,)


def test_returns_empty_result_for_missing_execution(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    assert recorder.get_latest(
        "missing"
    ) is None
    assert recorder.history(
        "missing"
    ) == ()


@pytest.mark.parametrize(
    "execution_id, error_type, message",
    (
        (
            object(),
            TypeError,
            "execution_id must be a string",
        ),
        (
            "   ",
            ValueError,
            "execution_id must not be empty",
        ),
    ),
)
def test_rejects_invalid_execution_id(
    tmp_path: Path,
    execution_id: object,
    error_type: type[Exception],
    message: str,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    with pytest.raises(
        error_type,
        match=message,
    ):
        recorder.history(execution_id)


@pytest.mark.parametrize(
    "payload, message",
    (
        (
            "not-json",
            "payload is not valid JSON",
        ),
        (
            json.dumps(
                {
                    "schema_version": 2,
                }
            ),
            "schema version is not supported",
        ),
    ),
)
def test_rejects_corrupt_stored_payload(
    tmp_path: Path,
    payload: str,
    message: str,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO experiment_execution_snapshots (
                execution_id,
                sequence,
                status,
                payload
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "corrupt",
                1,
                "PENDING",
                payload,
            ),
        )

    with pytest.raises(
        ValueError,
        match=message,
    ):
        recorder.get_latest("corrupt")


def test_is_exported_from_storage() -> None:
    assert (
        ExportedRecorder
        is SqliteExperimentExecutionRecorder
    )
