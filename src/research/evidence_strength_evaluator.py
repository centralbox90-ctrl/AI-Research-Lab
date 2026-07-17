from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class EvidenceStrengthEvaluator:
    """
    Формирует итоговую оценку силы научного evidence.

    Evaluator использует готовые результаты:

    - basic result validation;
    - statistical evaluation;
    - effect size;
    - robustness evaluation;
    - contradiction evaluation.

    Score является прозрачным research index в диапазоне 0.0–1.0.
    Он не является вероятностью истинности гипотезы и не заменяет
    HypothesisDecision.
    """

    VALIDATION_WEIGHT = 0.15
    SIGNIFICANCE_WEIGHT = 0.15
    P_VALUE_WEIGHT = 0.10
    EFFECT_SIZE_WEIGHT = 0.10
    ROBUSTNESS_WEIGHT = 0.25
    CONTRADICTION_WEIGHT = 0.25

    LARGE_EFFECT_SIZE = 0.80

    BASIS = (
        "Basic validation, statistical significance, p-value, "
        "effect size, robustness and contradiction evaluation"
    )

    def evaluate(
        self,
        experiment_evaluation: ExperimentEvaluation,
        statistical_evaluation: StatisticalEvaluation,
        robustness_evaluation: RobustnessEvaluation,
        contradiction_evaluation: ContradictionEvaluation,
    ) -> EvidenceStrengthEvaluation:
        warnings: list[str] = []

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

        if not experiment_id:
            warnings.append("Experiment ID is missing")

        if len(experiment_ids) > 1:
            warnings.append(
                "Evaluation objects belong to different experiments"
            )

            return EvidenceStrengthEvaluation(
                experiment_id=experiment_id,
                is_evaluated=False,
                score=0.0,
                level="unknown",
                warnings=warnings,
                basis=self.BASIS,
                notes=(
                    "Evidence strength requires evaluation objects "
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

            return EvidenceStrengthEvaluation(
                experiment_id=experiment_id,
                is_evaluated=False,
                score=0.0,
                level="unknown",
                result_is_valid=experiment_evaluation.is_valid,
                statistically_significant=(
                    statistical_evaluation.is_significant
                ),
                p_value=statistical_evaluation.p_value,
                effect_size=statistical_evaluation.effect_size,
                robust=robustness_evaluation.is_robust,
                has_contradiction=(
                    contradiction_evaluation.has_contradiction
                ),
                warnings=warnings,
                basis=self.BASIS,
                notes=(
                    "Evidence strength could not be completed because "
                    "one or more evaluation layers are incomplete."
                ),
            )

        validation_score = (
            1.0 if experiment_evaluation.is_valid else 0.0
        )

        significance_score = (
            1.0 if statistical_evaluation.is_significant else 0.0
        )

        p_value_score = self._calculate_p_value_score(
            p_value=statistical_evaluation.p_value,
            significance_level=(
                statistical_evaluation.significance_level
            ),
        )

        effect_size_score = self._calculate_effect_size_score(
            statistical_evaluation.effect_size
        )

        robustness_score = (
            1.0 if robustness_evaluation.is_robust else 0.0
        )

        contradiction_score = (
            0.0
            if contradiction_evaluation.has_contradiction
            else 1.0
        )

        component_scores = {
            "validation": validation_score,
            "statistical_significance": significance_score,
            "p_value_strength": p_value_score,
            "effect_size_strength": effect_size_score,
            "robustness": robustness_score,
            "contradiction_absence": contradiction_score,
        }

        score = (
            validation_score * self.VALIDATION_WEIGHT
            + significance_score * self.SIGNIFICANCE_WEIGHT
            + p_value_score * self.P_VALUE_WEIGHT
            + effect_size_score * self.EFFECT_SIZE_WEIGHT
            + robustness_score * self.ROBUSTNESS_WEIGHT
            + contradiction_score * self.CONTRADICTION_WEIGHT
        )

        score = max(0.0, min(1.0, float(score)))

        return EvidenceStrengthEvaluation(
            experiment_id=experiment_id,
            is_evaluated=True,
            score=score,
            level=self._resolve_level(score),
            result_is_valid=experiment_evaluation.is_valid,
            statistically_significant=(
                statistical_evaluation.is_significant
            ),
            p_value=statistical_evaluation.p_value,
            effect_size=statistical_evaluation.effect_size,
            robust=robustness_evaluation.is_robust,
            has_contradiction=(
                contradiction_evaluation.has_contradiction
            ),
            component_scores=component_scores,
            warnings=warnings,
            basis=self.BASIS,
            notes=(
                "Evidence strength was calculated as a weighted research "
                "index. The score is not a probability that the "
                "hypothesis is true."
            ),
        )

    @staticmethod
    def _calculate_p_value_score(
        p_value: float | None,
        significance_level: float | None,
    ) -> float:
        if (
            p_value is None
            or significance_level is None
            or significance_level <= 0.0
        ):
            return 0.0

        normalized_score = (
            significance_level - p_value
        ) / significance_level

        return max(0.0, min(1.0, float(normalized_score)))

    def _calculate_effect_size_score(
        self,
        effect_size: float | None,
    ) -> float:
        if effect_size is None:
            return 0.0

        normalized_score = (
            abs(effect_size) / self.LARGE_EFFECT_SIZE
        )

        return max(0.0, min(1.0, float(normalized_score)))

    @staticmethod
    def _resolve_level(score: float) -> str:
        if score < 0.25:
            return "very_weak"

        if score < 0.50:
            return "weak"

        if score < 0.75:
            return "moderate"

        if score < 0.90:
            return "strong"

        return "very_strong"