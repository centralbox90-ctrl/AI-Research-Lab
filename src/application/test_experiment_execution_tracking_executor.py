from datetime import UTC, datetime, timedelta

import pytest

from src.application.experiment_execution_tracking_executor import (
    ExperimentExecutionTrackingExecutor,
)
from src.research import (
    Experiment,
    ExperimentResult,
)
from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionStatus,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    12,
    0,
    tzinfo=UTC,
)
STARTED_AT = CREATED_AT + timedelta(seconds=1)
FINISHED_AT = STARTED_AT + timedelta(seconds=2)
SPECIFICATION_FINGERPRINT = "a" * 64
ENVIRONMENT_FINGERPRINT = "b" * 64


class SequenceClock:

    def __init__(
        self,
        *timestamps: datetime,
    ) -> None:
        self._timestamps = list(
            timestamps
        )

    def now(self) -> datetime:
        if not self._timestamps:
            raise AssertionError(
                "unexpected clock call"
            )

        return self._timestamps.pop(0)


class RecordingRecorder:

    def __init__(self) -> None:
        self.executions: list[
            ExperimentExecution
        ] = []

    def record(
        self,
        execution: ExperimentExecution,
    ) -> None:
        self.executions.append(
            execution
        )


class SuccessfulExecutor:

    def __init__(
        self,
        result: ExperimentResult,
    ) -> None:
        self.result = result
        self.call_count = 0

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        self.call_count += 1

        return self.result


class FailingExecutor:

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        raise RuntimeError(
            "executor failed"
        )


class InvalidResultExecutor:

    def __call__(
        self,
        experiment: Experiment,
    ) -> object:
        return object()


def build_execution() -> ExperimentExecution:
    return ExperimentExecution(
        execution_id="execution-id",
        experiment_id="experiment-id",
        specification_fingerprint=(
            SPECIFICATION_FINGERPRINT
        ),
        correlation_id="correlation-id",
        created_at=CREATED_AT,
    )


def build_experiment() -> Experiment:
    return Experiment(
        id="experiment-id",
        hypothesis_id="hypothesis-id",
        title="Experiment",
    )


def build_result() -> ExperimentResult:
    return ExperimentResult(
        id="result-id",
        experiment_id="experiment-id",
        success=True,
    )


def test_records_pending_running_and_succeeded_states(
) -> None:
    recorder = RecordingRecorder()
    delegate = SuccessfulExecutor(
        build_result()
    )
    tracking = ExperimentExecutionTrackingExecutor(
        executor=delegate,
        execution=build_execution(),
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        recorder=recorder,
        clock=SequenceClock(
            STARTED_AT,
            FINISHED_AT,
        ),
    )

    result = tracking(
        build_experiment()
    )

    assert result.id == "result-id"
    assert delegate.call_count == 1
    assert [
        execution.status
        for execution in recorder.executions
    ] == [
        ExperimentExecutionStatus.PENDING,
        ExperimentExecutionStatus.RUNNING,
        ExperimentExecutionStatus.SUCCEEDED,
    ]
    assert tracking.execution.status is (
        ExperimentExecutionStatus.SUCCEEDED
    )
    assert tracking.execution.result_id == "result-id"
    assert tracking.execution.started_at == STARTED_AT
    assert tracking.execution.finished_at == FINISHED_AT


def test_records_failed_state_and_reraises_executor_error(
) -> None:
    recorder = RecordingRecorder()
    tracking = ExperimentExecutionTrackingExecutor(
        executor=FailingExecutor(),
        execution=build_execution(),
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        recorder=recorder,
        clock=SequenceClock(
            STARTED_AT,
            FINISHED_AT,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="executor failed",
    ):
        tracking(
            build_experiment()
        )

    assert [
        execution.status
        for execution in recorder.executions
    ] == [
        ExperimentExecutionStatus.PENDING,
        ExperimentExecutionStatus.RUNNING,
        ExperimentExecutionStatus.FAILED,
    ]

    failed = tracking.execution

    assert failed.status is (
        ExperimentExecutionStatus.FAILED
    )
    assert failed.result_id is None
    assert failed.failure is not None
    assert failed.failure.error_type == "RuntimeError"
    assert failed.failure.message == "executor failed"


def test_invalid_executor_result_is_execution_failure(
) -> None:
    recorder = RecordingRecorder()
    tracking = ExperimentExecutionTrackingExecutor(
        executor=InvalidResultExecutor(),
        execution=build_execution(),
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        recorder=recorder,
        clock=SequenceClock(
            STARTED_AT,
            FINISHED_AT,
        ),
    )

    with pytest.raises(
        TypeError,
        match=(
            "executor must return an "
            "ExperimentResult"
        ),
    ):
        tracking(
            build_experiment()
        )

    assert tracking.execution.status is (
        ExperimentExecutionStatus.FAILED
    )
    assert tracking.execution.failure is not None
    assert tracking.execution.failure.error_type == (
        "TypeError"
    )


def test_downstream_failure_does_not_change_success(
) -> None:
    tracking = ExperimentExecutionTrackingExecutor(
        executor=SuccessfulExecutor(
            build_result()
        ),
        execution=build_execution(),
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        recorder=RecordingRecorder(),
        clock=SequenceClock(
            STARTED_AT,
            FINISHED_AT,
        ),
    )

    tracking(
        build_experiment()
    )

    with pytest.raises(
        RuntimeError,
        match="artifact persistence failed",
    ):
        raise RuntimeError(
            "artifact persistence failed"
        )

    assert tracking.execution.status is (
        ExperimentExecutionStatus.SUCCEEDED
    )


def test_tracking_executor_can_be_invoked_only_once(
) -> None:
    tracking = ExperimentExecutionTrackingExecutor(
        executor=SuccessfulExecutor(
            build_result()
        ),
        execution=build_execution(),
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        recorder=RecordingRecorder(),
        clock=SequenceClock(
            STARTED_AT,
            FINISHED_AT,
        ),
    )

    tracking(
        build_experiment()
    )

    with pytest.raises(
        RuntimeError,
        match="invoked only once",
    ):
        tracking(
            build_experiment()
        )


def test_requires_pending_execution() -> None:
    running = build_execution().start(
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        started_at=STARTED_AT,
    )

    with pytest.raises(
        ValueError,
        match="execution must be PENDING",
    ):
        ExperimentExecutionTrackingExecutor(
            executor=SuccessfulExecutor(
                build_result()
            ),
            execution=running,
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
            recorder=RecordingRecorder(),
            clock=SequenceClock(
                FINISHED_AT,
            ),
        )


def test_requires_recorder_contract() -> None:
    with pytest.raises(
        TypeError,
        match="recorder must provide",
    ):
        ExperimentExecutionTrackingExecutor(
            executor=SuccessfulExecutor(
                build_result()
            ),
            execution=build_execution(),
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
            recorder=object(),
            clock=SequenceClock(
                STARTED_AT,
                FINISHED_AT,
            ),
        )