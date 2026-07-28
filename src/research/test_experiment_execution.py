from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from src.research import (
    ExperimentExecution as ExportedExperimentExecution,
)
from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
    ExperimentExecutionStatus,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    10,
    0,
    tzinfo=timezone.utc,
)
STARTED_AT = CREATED_AT + timedelta(seconds=1)
FINISHED_AT = STARTED_AT + timedelta(seconds=2)
SPECIFICATION_FINGERPRINT = "a" * 64
ENVIRONMENT_FINGERPRINT = "b" * 64


def build_execution(
    **overrides: object,
) -> ExperimentExecution:
    values: dict[str, object] = {
        "execution_id": " execution-id ",
        "experiment_id": " experiment-id ",
        "specification_fingerprint": (
            SPECIFICATION_FINGERPRINT
        ),
        "created_at": CREATED_AT,
        "correlation_id": " correlation-id ",
    }
    values.update(overrides)

    return ExperimentExecution(**values)


def build_failure(
    stage: ExperimentExecutionFailureStage,
) -> ExperimentExecutionFailure:
    return ExperimentExecutionFailure(
        stage=stage,
        error_type=" RuntimeError ",
        message=" executor failed ",
    )


def test_pending_execution_normalizes_and_serializes() -> None:
    execution = build_execution()

    assert execution.execution_id == "execution-id"
    assert execution.experiment_id == "experiment-id"
    assert execution.correlation_id == "correlation-id"
    assert execution.status is (
        ExperimentExecutionStatus.PENDING
    )
    assert not execution.is_terminal

    assert execution.to_dict() == {
        "schema_version": 1,
        "execution_id": "execution-id",
        "experiment_id": "experiment-id",
        "specification_fingerprint": (
            SPECIFICATION_FINGERPRINT
        ),
        "correlation_id": "correlation-id",
        "environment_fingerprint": None,
        "status": "PENDING",
        "created_at": CREATED_AT.isoformat(),
        "started_at": None,
        "finished_at": None,
        "result_id": None,
        "failure": None,
    }


def test_is_exported_from_research_package() -> None:
    assert ExportedExperimentExecution is ExperimentExecution


def test_execution_is_immutable() -> None:
    execution = build_execution()

    with pytest.raises(FrozenInstanceError):
        execution.status = ExperimentExecutionStatus.RUNNING


def test_start_returns_new_running_execution() -> None:
    local_time = datetime(
        2026,
        7,
        28,
        12,
        0,
        1,
        tzinfo=timezone(timedelta(hours=2)),
    )
    pending = build_execution()

    running = pending.start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=local_time,
    )

    assert pending.status is (
        ExperimentExecutionStatus.PENDING
    )
    assert running.status is (
        ExperimentExecutionStatus.RUNNING
    )
    assert running.started_at == STARTED_AT
    assert running.environment_fingerprint == (
        ENVIRONMENT_FINGERPRINT
    )
    assert not running.is_terminal


def test_succeed_requires_running_execution() -> None:
    with pytest.raises(
        ValueError,
        match="RUNNING",
    ):
        build_execution().succeed(
            result_id="result-id",
            finished_at=FINISHED_AT,
        )


def test_succeed_returns_terminal_execution() -> None:
    running = build_execution().start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=STARTED_AT,
    )

    succeeded = running.succeed(
        result_id=" result-id ",
        finished_at=FINISHED_AT,
    )

    assert succeeded.status is (
        ExperimentExecutionStatus.SUCCEEDED
    )
    assert succeeded.result_id == "result-id"
    assert succeeded.finished_at == FINISHED_AT
    assert succeeded.failure is None
    assert succeeded.is_terminal


def test_fail_pending_execution_during_preparation() -> None:
    failure = build_failure(
        ExperimentExecutionFailureStage.PREPARATION
    )

    failed = build_execution().fail(
        failure=failure,
        finished_at=FINISHED_AT,
    )

    assert failed.status is (
        ExperimentExecutionStatus.FAILED
    )
    assert failed.started_at is None
    assert failed.result_id is None
    assert failed.failure is failure
    assert failed.failure.to_dict() == {
        "stage": "PREPARATION",
        "error_type": "RuntimeError",
        "message": "executor failed",
    }


def test_fail_running_execution_during_execution() -> None:
    running = build_execution().start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=STARTED_AT,
    )
    failure = build_failure(
        ExperimentExecutionFailureStage.EXECUTION
    )

    failed = running.fail(
        failure=failure,
        finished_at=FINISHED_AT,
    )

    assert failed.status is (
        ExperimentExecutionStatus.FAILED
    )
    assert failed.started_at == STARTED_AT
    assert failed.failure is failure
    assert failed.is_terminal


@pytest.mark.parametrize(
    "start_first",
    (False, True),
)
def test_cancel_pending_or_running_execution(
    start_first: bool,
) -> None:
    execution = build_execution()

    if start_first:
        execution = execution.start(
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
            started_at=STARTED_AT,
        )

    cancelled = execution.cancel(
        finished_at=FINISHED_AT,
    )

    assert cancelled.status is (
        ExperimentExecutionStatus.CANCELLED
    )
    assert cancelled.result_id is None
    assert cancelled.failure is None
    assert cancelled.is_terminal


def test_rejects_failure_stage_for_wrong_state() -> None:
    with pytest.raises(
        ValueError,
        match="failure stage",
    ):
        build_execution().fail(
            failure=build_failure(
                ExperimentExecutionFailureStage.EXECUTION
            ),
            finished_at=FINISHED_AT,
        )


def test_terminal_execution_cannot_transition() -> None:
    terminal = (
        build_execution()
        .start(
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
            started_at=STARTED_AT,
        )
        .succeed(
            result_id="result-id",
            finished_at=FINISHED_AT,
        )
    )

    with pytest.raises(
        ValueError,
        match="PENDING, RUNNING",
    ):
        terminal.cancel(
            finished_at=FINISHED_AT,
        )


@pytest.mark.parametrize(
    "fingerprint",
    (
        "a" * 63,
        "A" * 64,
        "g" * 64,
        "",
    ),
)
def test_rejects_invalid_specification_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="specification_fingerprint",
    ):
        build_execution(
            specification_fingerprint=fingerprint,
        )


def test_rejects_naive_timestamp() -> None:
    with pytest.raises(
        ValueError,
        match="created_at must be timezone-aware",
    ):
        build_execution(
            created_at=datetime(2026, 7, 28, 10, 0),
        )


def test_rejects_reversed_timeline() -> None:
    running = build_execution().start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=STARTED_AT,
    )

    with pytest.raises(
        ValueError,
        match="finished_at must not be earlier",
    ):
        running.succeed(
            result_id="result-id",
            finished_at=CREATED_AT,
        )


def test_rejects_direct_invalid_running_state() -> None:
    with pytest.raises(
        ValueError,
        match="RUNNING execution requires",
    ):
        build_execution(
            status=ExperimentExecutionStatus.RUNNING,
        )


def test_rejects_string_status() -> None:
    with pytest.raises(
        TypeError,
        match="ExperimentExecutionStatus",
    ):
        build_execution(
            status="PENDING",
        )


def test_failure_requires_typed_stage() -> None:
    with pytest.raises(
        TypeError,
        match="ExperimentExecutionFailureStage",
    ):
        ExperimentExecutionFailure(
            stage="EXECUTION",
            error_type="RuntimeError",
            message="failed",
        )