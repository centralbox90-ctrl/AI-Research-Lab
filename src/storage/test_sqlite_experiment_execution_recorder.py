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
    pending = build_pending()
    running = build_running()
    succeeded = build_succeeded()
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )

    recorder.record(pending)
    recorder.record(running)
    recorder.record(succeeded)

    reopened = SqliteExperimentExecutionRecorder(
        db_path
    )

    assert reopened.get_latest(
        succeeded.execution_id
    ) == succeeded


def test_round_trips_failure(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()
    running = build_running()
    failed = running.fail(
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

    recorder.record(pending)
    recorder.record(running)
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


def test_lists_execution_ids_deterministically(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    recorder.record(
        build_pending("execution-2")
    )
    recorder.record(
        build_pending("execution-1")
    )
    recorder.record(
        build_running("execution-1")
    )

    assert recorder.list_execution_ids() == (
        "execution-1",
        "execution-2",
    )


def test_lists_no_execution_ids_for_empty_storage(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    assert recorder.list_execution_ids() == ()


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

def test_rejects_non_pending_first_snapshot(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )

    with pytest.raises(
        ValueError,
        match=(
            "first execution snapshot "
            "must be PENDING"
        ),
    ):
        recorder.record(
            build_running()
        )

    assert recorder.list_execution_ids() == ()


def test_rejects_skipped_execution_transition(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()
    succeeded = build_succeeded()

    recorder.record(pending)

    with pytest.raises(
        ValueError,
        match=(
            "invalid execution status transition: "
            "PENDING -> SUCCEEDED"
        ),
    ):
        recorder.record(succeeded)

    assert recorder.history(
        pending.execution_id
    ) == (pending,)


def test_rejects_duplicate_execution_snapshot(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()

    recorder.record(pending)

    with pytest.raises(
        ValueError,
        match=(
            "invalid execution status transition: "
            "PENDING -> PENDING"
        ),
    ):
        recorder.record(pending)

    assert recorder.history(
        pending.execution_id
    ) == (pending,)


def test_rejects_snapshot_after_terminal_state(
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

    with pytest.raises(
        ValueError,
        match=(
            "terminal execution cannot accept "
            "another snapshot"
        ),
    ):
        recorder.record(succeeded)

    assert recorder.history(
        succeeded.execution_id
    ) == (
        pending,
        running,
        succeeded,
    )


def test_rejects_changed_execution_identity(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()
    changed_pending = ExperimentExecution(
        execution_id=pending.execution_id,
        experiment_id="different-experiment",
        specification_fingerprint=(
            pending.specification_fingerprint
        ),
        correlation_id=pending.correlation_id,
        created_at=pending.created_at,
    )
    changed_running = changed_pending.start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=(
            CREATED_AT
            + timedelta(seconds=1)
        ),
    )

    recorder.record(pending)

    with pytest.raises(
        ValueError,
        match=(
            "experiment_id must not change "
            "between execution snapshots"
        ),
    ):
        recorder.record(changed_running)

    assert recorder.history(
        pending.execution_id
    ) == (pending,)


def test_rejects_changed_running_context(
    tmp_path: Path,
) -> None:
    recorder = SqliteExperimentExecutionRecorder(
        tmp_path / "executions.db"
    )
    pending = build_pending()
    running = build_running()
    changed_running = pending.start(
        environment_fingerprint="c" * 64,
        started_at=(
            CREATED_AT
            + timedelta(seconds=1)
        ),
    )
    changed_succeeded = changed_running.succeed(
        result_id="execution-1-result",
        finished_at=(
            CREATED_AT
            + timedelta(seconds=2)
        ),
    )

    recorder.record(pending)
    recorder.record(running)

    with pytest.raises(
        ValueError,
        match=(
            "environment_fingerprint must not "
            "change after execution starts"
        ),
    ):
        recorder.record(changed_succeeded)

    assert recorder.history(
        pending.execution_id
    ) == (
        pending,
        running,
    )

def insert_raw_snapshot(
    db_path: Path,
    *,
    execution_id: str,
    sequence: int,
    status: str,
    snapshot: ExperimentExecution,
) -> None:
    payload = json.dumps(
        snapshot.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
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
                execution_id,
                sequence,
                status,
                payload,
            ),
        )


def test_rejects_stored_history_with_sequence_gap(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending()

    insert_raw_snapshot(
        db_path,
        execution_id=pending.execution_id,
        sequence=2,
        status=pending.status.value,
        snapshot=pending,
    )

    with pytest.raises(
        ValueError,
        match=(
            "stored execution history must "
            "start at sequence 1"
        ),
    ):
        recorder.history(
            pending.execution_id
        )


def test_rejects_stored_status_mismatch(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending()

    insert_raw_snapshot(
        db_path,
        execution_id=pending.execution_id,
        sequence=1,
        status="RUNNING",
        snapshot=pending,
    )

    with pytest.raises(
        ValueError,
        match=(
            "stored execution status does not "
            "match payload"
        ),
    ):
        recorder.history(
            pending.execution_id
        )


def test_rejects_stored_execution_id_mismatch(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending()

    insert_raw_snapshot(
        db_path,
        execution_id="stored-execution",
        sequence=1,
        status=pending.status.value,
        snapshot=pending,
    )

    with pytest.raises(
        ValueError,
        match=(
            "stored execution_id does not "
            "match payload"
        ),
    ):
        recorder.history(
            "stored-execution"
        )


def test_rejects_non_pending_stored_history(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    running = build_running()

    insert_raw_snapshot(
        db_path,
        execution_id=running.execution_id,
        sequence=1,
        status=running.status.value,
        snapshot=running,
    )

    with pytest.raises(
        ValueError,
        match=(
            "stored execution history must "
            "start with PENDING"
        ),
    ):
        recorder.history(
            running.execution_id
        )


def test_rejects_invalid_stored_transition(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending()
    succeeded = build_succeeded()

    insert_raw_snapshot(
        db_path,
        execution_id=pending.execution_id,
        sequence=1,
        status=pending.status.value,
        snapshot=pending,
    )
    insert_raw_snapshot(
        db_path,
        execution_id=succeeded.execution_id,
        sequence=2,
        status=succeeded.status.value,
        snapshot=succeeded,
    )

    with pytest.raises(
        ValueError,
        match=(
            "invalid execution status transition: "
            "PENDING -> SUCCEEDED"
        ),
    ):
        recorder.history(
            pending.execution_id
        )

def test_get_latest_rejects_invalid_stored_history(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending()
    succeeded = build_succeeded()

    insert_raw_snapshot(
        db_path,
        execution_id=pending.execution_id,
        sequence=1,
        status=pending.status.value,
        snapshot=pending,
    )
    insert_raw_snapshot(
        db_path,
        execution_id=succeeded.execution_id,
        sequence=2,
        status=succeeded.status.value,
        snapshot=succeeded,
    )

    with pytest.raises(
        ValueError,
        match=(
            "invalid execution status transition: "
            "PENDING -> SUCCEEDED"
        ),
    ):
        recorder.get_latest(
            pending.execution_id
        )

def test_rejects_listing_with_corrupt_stored_history(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "executions.db"
    recorder = SqliteExperimentExecutionRecorder(
        db_path
    )
    pending = build_pending(
        "corrupt-listing-execution"
    )

    insert_raw_snapshot(
        db_path,
        execution_id=pending.execution_id,
        sequence=2,
        status=pending.status.value,
        snapshot=pending,
    )

    with pytest.raises(
        ValueError,
        match=(
            "stored execution history must "
            "start at sequence 1"
        ),
    ):
        recorder.list_execution_ids()
