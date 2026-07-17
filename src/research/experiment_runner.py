from datetime import datetime
from typing import Callable

from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.research_types import ExperimentStatus


class ExperimentRunner:
    """
    Запускает исследовательский эксперимент.
    """

    def run(
        self,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> ExperimentResult:
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()

        try:
            result = executor(experiment)

            if result.experiment_id != experiment.id:
                result.experiment_id = experiment.id

            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now()

            return result

        except Exception:
            experiment.status = ExperimentStatus.FAILED
            experiment.completed_at = datetime.now()
            raise