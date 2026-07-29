from __future__ import annotations

import json

from src.application.get_experiment_execution_history import (
    GetExperimentExecutionHistory,
)


class GetExperimentExecutionHistoryCommand:
    """Renders one technical execution history as versioned JSON."""

    def __init__(
        self,
        *,
        application: GetExperimentExecutionHistory,
    ) -> None:
        if not isinstance(
            application,
            GetExperimentExecutionHistory,
        ):
            raise TypeError(
                "application must be a "
                "GetExperimentExecutionHistory"
            )

        self._application = application

    def execute(
        self,
        execution_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        history = self._application.execute(
            execution_id
        )

        if not history:
            return None

        payload = {
            "schema_version": 1,
            "execution_id": (
                history[0].execution_id
            ),
            "snapshot_count": len(history),
            "snapshots": [
                snapshot.to_dict()
                for snapshot in history
            ],
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
