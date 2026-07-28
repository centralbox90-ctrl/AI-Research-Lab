from __future__ import annotations

from src.application.experiment_execution_recorder import (
    ExperimentExecutionRecorder,
)
from src.application.market_experiment_executor import (
    MarketExperimentExecutor,
)
from src.application.ports.clock import Clock
from src.research import (
    Experiment,
    ExperimentResult,
)
from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
    ExperimentExecutionStatus,
)


class ExperimentExecutionTrackingExecutor:
    """
    Records technical execution states around one executor invocation.

    SUCCEEDED is recorded immediately after a valid ExperimentResult is
    returned. Downstream evaluation and artifact persistence are outside
    this adapter and cannot change the execution outcome.
    """

    def __init__(
        self,
        *,
        executor: MarketExperimentExecutor,
        execution: ExperimentExecution,
        environment_fingerprint: str,
        recorder: ExperimentExecutionRecorder,
        clock: Clock,
    ) -> None:
        if not callable(executor):
            raise TypeError(
                "executor must be callable"
            )

        if not isinstance(
            execution,
            ExperimentExecution,
        ):
            raise TypeError(
                "execution must be an "
                "ExperimentExecution"
            )

        if (
            execution.status
            is not ExperimentExecutionStatus.PENDING
        ):
            raise ValueError(
                "execution must be PENDING"
            )

        if not callable(
            getattr(recorder, "record", None)
        ):
            raise TypeError(
                "recorder must provide a callable "
                "record method"
            )

        if not callable(
            getattr(clock, "now", None)
        ):
            raise TypeError(
                "clock must provide a callable now method"
            )

        self._executor = executor
        self._execution = execution
        self._environment_fingerprint = (
            environment_fingerprint
        )
        self._recorder = recorder
        self._clock = clock

    @property
    def execution(self) -> ExperimentExecution:
        return self._execution

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        if (
            self._execution.status
            is not ExperimentExecutionStatus.PENDING
        ):
            raise RuntimeError(
                "tracking executor can be invoked only once"
            )

        self._recorder.record(
            self._execution
        )

        running = self._execution.start(
            environment_fingerprint=(
                self._environment_fingerprint
            ),
            started_at=self._clock.now(),
        )
        self._execution = running
        self._recorder.record(running)

        try:
            result = self._executor(
                experiment
            )

            if not isinstance(
                result,
                ExperimentResult,
            ):
                raise TypeError(
                    "executor must return an "
                    "ExperimentResult"
                )

            succeeded = running.succeed(
                result_id=result.id,
                finished_at=self._clock.now(),
            )
        except Exception as error:
            failure = ExperimentExecutionFailure(
                stage=(
                    ExperimentExecutionFailureStage.EXECUTION
                ),
                error_type=type(error).__name__,
                message=(
                    str(error).strip()
                    or type(error).__name__
                ),
            )
            failed = running.fail(
                failure=failure,
                finished_at=self._clock.now(),
            )
            self._execution = failed
            self._recorder.record(failed)
            raise

        self._execution = succeeded
        self._recorder.record(succeeded)

        return result