from typing import Protocol

from src.research.experiment_execution import (
    ExperimentExecution,
)


class ExperimentExecutionHistoryReader(Protocol):
    """Application port for reading append-only execution history."""

    def history(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        """Return snapshots in their persisted sequence."""
