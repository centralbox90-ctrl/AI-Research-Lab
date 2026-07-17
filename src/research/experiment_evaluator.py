import math
from numbers import Real

from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.experiment_result import ExperimentResult


class ExperimentEvaluator:
    """
    Выполняет базовую валидацию результата эксперимента.

    Этот класс пока не оценивает статистическую значимость,
    устойчивость или поддержку гипотезы.
    """

    def evaluate(
        self,
        result: ExperimentResult,
    ) -> ExperimentEvaluation:
        warnings: list[str] = []

        if not result.experiment_id:
            warnings.append("Experiment ID is missing")

        if not result.metrics:
            warnings.append("Metrics are missing")

        for metric_name, metric_value in result.metrics.items():
            if (
                isinstance(metric_value, bool)
                or not isinstance(metric_value, Real)
            ):
                warnings.append(
                    f"Metric '{metric_name}' is not numeric"
                )
                continue

            if not math.isfinite(float(metric_value)):
                warnings.append(
                    f"Metric '{metric_name}' is not finite"
                )

        is_valid = len(warnings) == 0

        notes = (
            "Result passed basic validation. "
            "Statistical and robustness evaluation are not implemented."
            if is_valid
            else "Result failed basic validation."
        )

        return ExperimentEvaluation(
            experiment_id=result.experiment_id,
            is_valid=is_valid,
            evidence_strength=0.0,
            warnings=warnings,
            notes=notes,
        )