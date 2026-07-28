from typing import Protocol

from src.research.experiment_execution import (
    ExperimentExecution,
)


class ExperimentExecutionRecorder(Protocol):
    """Application port for recording execution state snapshots."""

    def record(
        self,
        execution: ExperimentExecution,
    ) -> None:
        """Persist the supplied valid execution state."""