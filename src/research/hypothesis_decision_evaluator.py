from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.hypothesis_decision import HypothesisDecision
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class HypothesisDecisionEvaluator:
    """
    Формирует итоговое решение о поддержке гипотезы.

    Evaluator использует уже готовые evaluation objects и не выполняет
    повторных статистических или robustness расчётов.

    Строгое правило поддержки:

    - experiment result прошёл basic validation;
    - результат статистически значим;
    - результат robust;
    - противоречия отсутствуют.
    """

    BASIS = (
        "Basic validation, inferential statistics, robustness "
        "and contradiction evaluation"
    )

    def evaluate(
        self,
        hypothesis_id: str,
        experiment_evaluation: ExperimentEvaluation,
        statistical_evaluation: StatisticalEvaluation,
        robustness_evaluation: RobustnessEvaluation,
        contradiction_evaluation: ContradictionEvaluation,
    ) -> HypothesisDecision:
        warnings: list[str] = []
        failed_requirements: list[str] = []

        experiment_ids = {
            experiment_id
            for experiment_id in (
                experiment_evaluation.experiment_id,
                statistical_evaluation.experiment_id,
                robustness_evaluation.experiment_id,
                contradiction_evaluation.experiment_id,
            )
            if experiment_id
        }

        experiment_id = next(iter(experiment_ids), "")

        if not hypothesis_id:
            warnings.append("Hypothesis ID is missing")

        if not experiment_id:
            warnings.append("Experiment ID is missing")

        if len(experiment_ids) > 1:
            warnings.append(
                "Evaluation objects belong to different experiments"
            )

            return HypothesisDecision(
                experiment_id=experiment_id,
                hypothesis_id=hypothesis_id,
                is_evaluated=False,
                is_supported=False,
                warnings=warnings,
                basis=self.BASIS,
                notes=(
                    "Hypothesis decision requires evaluation objects "
                    "from the same experiment."
                ),
            )

        incomplete_layers: list[str] = []

        if not statistical_evaluation.is_evaluated:
            incomplete_layers.append("statistical evaluation")

        if not robustness_evaluation.is_evaluated:
            incomplete_layers.append("robustness evaluation")

        if not contradiction_evaluation.is_evaluated:
            incomplete_layers.append("contradiction evaluation")

        if incomplete_layers:
            warnings.append(
                "Incomplete evaluation layers: "
                + ", ".join(incomplete_layers)
            )

            return HypothesisDecision(
                experiment_id=experiment_id,
                hypothesis_id=hypothesis_id,
                is_evaluated=False,
                is_supported=False,
                result_is_valid=experiment_evaluation.is_valid,
                statistically_significant=(
                    statistical_evaluation.is_significant
                ),
                robust=robustness_evaluation.is_robust,
                has_contradiction=(
                    contradiction_evaluation.has_contradiction
                ),
                warnings=warnings,
                basis=self.BASIS,
                notes=(
                    "Hypothesis decision could not be completed because "
                    "one or more evaluation layers are incomplete."
                ),
            )

        result_is_valid = experiment_evaluation.is_valid
        statistically_significant = (
            statistical_evaluation.is_significant
        )
        robust = robustness_evaluation.is_robust
        has_contradiction = (
            contradiction_evaluation.has_contradiction
        )

        if not result_is_valid:
            failed_requirements.append(
                "Experiment result failed basic validation"
            )

        if not statistically_significant:
            failed_requirements.append(
                "Result is not statistically significant"
            )

        if not robust:
            failed_requirements.append(
                "Result is not robust"
            )

        if has_contradiction:
            failed_requirements.append(
                "Contradictions were detected"
            )

        is_supported = len(failed_requirements) == 0

        satisfied_requirements = 4 - len(failed_requirements)
        confidence = satisfied_requirements / 4.0

        return HypothesisDecision(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            is_evaluated=True,
            is_supported=is_supported,
            result_is_valid=result_is_valid,
            statistically_significant=statistically_significant,
            robust=robust,
            has_contradiction=has_contradiction,
            confidence=float(confidence),
            failed_requirements=failed_requirements,
            warnings=warnings,
            basis=self.BASIS,
            notes=(
                "Hypothesis support was evaluated using basic validation, "
                "statistical significance, robustness and contradiction "
                "checks."
            ),
        )