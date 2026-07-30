from __future__ import annotations

from src.application.experiment_execution_catalog import (
    ExperimentExecutionCatalog,
)


class ListExperimentExecutions:
    """Returns persisted technical execution identities."""

    def __init__(
        self,
        *,
        catalog: ExperimentExecutionCatalog,
    ) -> None:
        if not callable(
            getattr(
                catalog,
                "list_execution_ids",
                None,
            )
        ):
            raise TypeError(
                "catalog must provide "
                "list_execution_ids"
            )

        self._catalog = catalog

    def execute(
        self,
    ) -> tuple[str, ...]:
        execution_ids = (
            self._catalog.list_execution_ids()
        )

        if not isinstance(execution_ids, tuple):
            raise TypeError(
                "execution IDs must be a tuple"
            )

        normalized: list[str] = []

        for execution_id in execution_ids:
            if not isinstance(execution_id, str):
                raise TypeError(
                    "each execution ID must be a string"
                )

            item = execution_id.strip()

            if not item:
                raise ValueError(
                    "execution ID must not be empty"
                )

            normalized.append(item)

        if len(normalized) != len(
            set(normalized)
        ):
            raise ValueError(
                "execution IDs must be unique"
            )

        return tuple(sorted(normalized))
