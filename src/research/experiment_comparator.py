from dataclasses import dataclass

from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult


@dataclass
class RankedExperiment:
    experiment: Experiment
    result: ExperimentResult
    score: float


class ExperimentComparator:
    """
    Сравнивает результаты экспериментов по выбранной метрике.
    """

    def rank(
        self,
        experiments: list[Experiment],
        results: list[ExperimentResult],
        metric: str,
        reverse: bool = True,
    ) -> list[RankedExperiment]:
        if len(experiments) != len(results):
            raise ValueError(
                "Experiments and results must have the same length."
            )

        ranked = [
            RankedExperiment(
                experiment=experiment,
                result=result,
                score=float(result.metrics.get(metric, 0.0)),
            )
            for experiment, result in zip(
                experiments,
                results,
                strict=True,
            )
        ]

        return sorted(
            ranked,
            key=lambda item: item.score,
            reverse=reverse,
        )

    def best(
        self,
        experiments: list[Experiment],
        results: list[ExperimentResult],
        metric: str,
        reverse: bool = True,
    ) -> RankedExperiment:
        ranked = self.rank(
            experiments=experiments,
            results=results,
            metric=metric,
            reverse=reverse,
        )

        if not ranked:
            raise ValueError("No experiments to compare.")

        return ranked[0]