from __future__ import annotations

from src.application.experiment_execution_history_reader import (
    ExperimentExecutionHistoryReader,
)
from src.research.experiment_execution import (
    ExperimentExecution,
)


class GetExperimentExecutionHistory:
    """Returns the validated history of one technical execution."""

    def __init__(
        self,
        *,
        reader: ExperimentExecutionHistoryReader,
    ) -> None:
        if not callable(
            getattr(reader, "history", None)
        ):
            raise TypeError(
                "reader must provide history"
            )

        self._reader = reader

    def execute(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        normalized_id = self._normalize_execution_id(
            execution_id
        )
        history = self._reader.history(
            normalized_id
        )

        if not isinstance(history, tuple):
            raise TypeError(
                "execution history must be a tuple"
            )

        if any(
            not isinstance(
                snapshot,
                ExperimentExecution,
            )
            for snapshot in history
        ):
            raise TypeError(
                "execution history must contain "
                "ExperimentExecution values"
            )

        if any(
            snapshot.execution_id != normalized_id
            for snapshot in history
        ):
            raise ValueError(
                "execution history contains a "
                "different execution_id"
            )

        return history

    @staticmethod
    def _normalize_execution_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "execution_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "execution_id must not be empty"
            )

        return normalized
