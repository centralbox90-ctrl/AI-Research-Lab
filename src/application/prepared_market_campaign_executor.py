from __future__ import annotations

from collections.abc import Callable

from src.research import (
    Experiment,
    ExperimentResult,
)


class PreparedMarketCampaignExecutor:
    """
    Routes each campaign experiment to its prepared executor.
    """

    def __init__(
        self,
        executors_by_experiment_id: dict[
            str,
            Callable[[Experiment], ExperimentResult],
        ],
    ) -> None:
        self._executors_by_experiment_id = dict(
            executors_by_experiment_id
        )

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        try:
            executor = self._executors_by_experiment_id[
                experiment.id
            ]
        except KeyError as error:
            raise ValueError(
                "no prepared executor for experiment"
            ) from error

        return executor(experiment)
