from __future__ import annotations

from typing import Protocol

from src.research.experiment_execution import (
    ExperimentExecution,
)


class ExperimentExecutionLister(Protocol):
    def execute(self) -> tuple[str, ...]:
        ...


class ExperimentExecutionHistoryGetter(Protocol):
    def execute(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        ...


class GetExperimentExecutionHistoryForResult:
    """
    Finds one validated technical execution history by result identity.

    Representation compatibility is delegated to the existing public
    execution use cases. Duplicate result references fail closed.
    """

    def __init__(
        self,
        *,
        execution_lister: ExperimentExecutionLister,
        history_getter: ExperimentExecutionHistoryGetter,
    ) -> None:
        if not callable(
            getattr(
                execution_lister,
                "execute",
                None,
            )
        ):
            raise TypeError(
                "execution_lister must provide execute"
            )

        if not callable(
            getattr(
                history_getter,
                "execute",
                None,
            )
        ):
            raise TypeError(
                "history_getter must provide execute"
            )

        self._execution_lister = execution_lister
        self._history_getter = history_getter

    def execute(
        self,
        result_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        normalized_result_id = (
            self._normalize_result_id(
                result_id
            )
        )
        matches: list[
            tuple[ExperimentExecution, ...]
        ] = []

        for execution_id in (
            self._execution_lister.execute()
        ):
            history = self._history_getter.execute(
                execution_id
            )

            if (
                history
                and history[-1].result_id
                == normalized_result_id
            ):
                matches.append(history)

        if len(matches) > 1:
            raise ValueError(
                "multiple execution histories reference "
                f"result_id: {normalized_result_id}"
            )

        if not matches:
            return ()

        return matches[0]

    @staticmethod
    def _normalize_result_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "result_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "result_id must not be empty"
            )

        return normalized
