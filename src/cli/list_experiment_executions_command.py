from __future__ import annotations

import json

from src.application.list_experiment_executions import (
    ListExperimentExecutions,
)


class ListExperimentExecutionsCommand:
    """Renders persisted execution identities as versioned JSON."""

    def __init__(
        self,
        *,
        application: ListExperimentExecutions,
    ) -> None:
        if not isinstance(
            application,
            ListExperimentExecutions,
        ):
            raise TypeError(
                "application must be a "
                "ListExperimentExecutions"
            )

        self._application = application

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        execution_ids = (
            self._application.execute()
        )
        payload = {
            "schema_version": 1,
            "execution_count": len(
                execution_ids
            ),
            "execution_ids": list(
                execution_ids
            ),
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
