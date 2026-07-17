from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class ContradictionEvaluator:
    """
    Выявляет противоречия между statistical и robustness signals.

    Evaluator не выполняет повторный статистический расчёт
    и не определяет, подтверждена ли исследовательская гипотеза.

    Текущие проверки:

    - статистически значимый результат не является robust;
    - направление общего среднего противоположно устойчивому
      направлению первой и второй половины наблюдений.
    """

    def evaluate(
        self,
        statistical_evaluation: StatisticalEvaluation,
        robustness_evaluation: RobustnessEvaluation,
    ) -> ContradictionEvaluation:
        warnings: list[str] = []

        experiment_id = (
            statistical_evaluation.experiment_id
            or robustness_evaluation.experiment_id
        )

        if not statistical_evaluation.experiment_id:
            warnings.append(
                "Statistical evaluation experiment ID is missing"
            )

        if not robustness_evaluation.experiment_id:
            warnings.append(
                "Robustness evaluation experiment ID is missing"
            )

        if (
            statistical_evaluation.experiment_id
            and robustness_evaluation.experiment_id
            and statistical_evaluation.experiment_id
            != robustness_evaluation.experiment_id
        ):
            warnings.append(
                "Statistical and robustness evaluations belong "
                "to different experiments"
            )

            return ContradictionEvaluation(
                experiment_id=experiment_id,
                is_evaluated=False,
                has_contradiction=False,
                warnings=warnings,
                notes=(
                    "Contradiction evaluation requires statistical "
                    "and robustness evaluations from the same experiment."
                ),
            )

        if not statistical_evaluation.is_evaluated:
            warnings.append(
                "Statistical evaluation is incomplete"
            )

        if not robustness_evaluation.is_evaluated:
            warnings.append(
                "Robustness evaluation is incomplete"
            )

        if (
            not statistical_evaluation.is_evaluated
            or not robustness_evaluation.is_evaluated
        ):
            return ContradictionEvaluation(
                experiment_id=experiment_id,
                is_evaluated=False,
                has_contradiction=False,
                statistically_significant=(
                    statistical_evaluation.is_significant
                ),
                robust=robustness_evaluation.is_robust,
                warnings=warnings,
                notes=(
                    "Contradiction evaluation requires completed "
                    "statistical and robustness evaluations."
                ),
            )

        observed_direction = self._direction(
            statistical_evaluation.mean
        )

        robustness_direction = self._resolve_robustness_direction(
            robustness_evaluation
        )

        significance_robustness_conflict = (
            statistical_evaluation.is_significant
            and not robustness_evaluation.is_robust
        )

        direction_robustness_conflict = (
            observed_direction in {"positive", "negative"}
            and robustness_direction in {"positive", "negative"}
            and observed_direction != robustness_direction
        )

        contradiction_count = sum(
            (
                significance_robustness_conflict,
                direction_robustness_conflict,
            )
        )

        has_contradiction = contradiction_count > 0

        return ContradictionEvaluation(
            experiment_id=experiment_id,
            is_evaluated=True,
            has_contradiction=has_contradiction,
            observed_direction=observed_direction,
            statistically_significant=(
                statistical_evaluation.is_significant
            ),
            robust=robustness_evaluation.is_robust,
            significance_robustness_conflict=(
                significance_robustness_conflict
            ),
            direction_robustness_conflict=(
                direction_robustness_conflict
            ),
            contradiction_count=contradiction_count,
            warnings=warnings,
            notes=(
                "Statistical significance, robustness and result "
                "direction were checked for contradictions."
            ),
        )

    @staticmethod
    def _direction(value: float | None) -> str:
        if value is None:
            return "unknown"

        if value > 0.0:
            return "positive"

        if value < 0.0:
            return "negative"

        return "zero"

    def _resolve_robustness_direction(
        self,
        evaluation: RobustnessEvaluation,
    ) -> str:
        if evaluation.direction_consistent is not True:
            return "unknown"

        first_direction = self._direction(
            evaluation.first_half_mean
        )
        second_direction = self._direction(
            evaluation.second_half_mean
        )

        if first_direction == second_direction:
            return first_direction

        return "unknown"