from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.hypothesis_decision import HypothesisDecision
from src.research.next_experiment_selection import (
    NextExperimentSelection,
)
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


class NextExperimentSelector:
    """
    Выбирает наиболее полезное следующее исследовательское действие.

    Selector использует gaps уже выполненного scientific pipeline.
    Он не принимает решение о поддержке гипотезы и не ранжирует
    эксперименты по качеству.
    """

    BASIS = (
        "Statistical evaluation, robustness evaluation, evidence "
        "strength and failed hypothesis decision requirements"
    )

    MINIMUM_SAMPLE_SIZE = 5

    def select(
        self,
        hypothesis_id: str,
        statistical_evaluation: StatisticalEvaluation,
        robustness_evaluation: RobustnessEvaluation,
        evidence_strength_evaluation: EvidenceStrengthEvaluation,
        hypothesis_decision: HypothesisDecision,
    ) -> NextExperimentSelection:
        warnings: list[str] = []

        if not hypothesis_id:
            warnings.append("Hypothesis ID is missing")

        failed_requirements = list(
            hypothesis_decision.failed_requirements
        )

        common_fields = {
            "hypothesis_id": hypothesis_id,
            "evidence_strength_score": (
                evidence_strength_evaluation.score
            ),
            "evidence_strength_level": (
                evidence_strength_evaluation.level
            ),
            "failed_requirements": failed_requirements,
            "warnings": warnings,
            "basis": self.BASIS,
        }

        if not statistical_evaluation.is_evaluated:
            return NextExperimentSelection(
                is_selected=True,
                action="collect_observations",
                priority="critical",
                reason=(
                    "Statistical evaluation could not be completed "
                    "because suitable raw observations are unavailable."
                ),
                target_requirement="statistical_evaluation",
                recommendations=[
                    "Collect numeric raw observations.",
                    "Store observations in ExperimentResult.observations.",
                    "Repeat the experiment with measurable outcomes.",
                ],
                notes=(
                    "Raw observations are required before inferential "
                    "statistics can guide the next research cycle."
                ),
                **common_fields,
            )

        sample_size = statistical_evaluation.sample_size

        if (
            sample_size is not None
            and sample_size < self.MINIMUM_SAMPLE_SIZE
        ):
            return NextExperimentSelection(
                is_selected=True,
                action="increase_sample_size",
                priority="high",
                reason=(
                    "The current sample size is too small for the "
                    "configured research continuation policy."
                ),
                target_requirement="sample_size",
                recommendations=[
                    (
                        "Collect at least "
                        f"{self.MINIMUM_SAMPLE_SIZE} numeric observations."
                    ),
                    "Repeat the same experimental protocol.",
                    "Avoid changing multiple experimental factors.",
                ],
                notes=(
                    "The next cycle should increase observation count "
                    "before changing the research hypothesis."
                ),
                **common_fields,
            )

        if not statistical_evaluation.is_significant:
            return NextExperimentSelection(
                is_selected=True,
                action="improve_statistical_significance",
                priority="high",
                reason=(
                    "The observed result does not meet the configured "
                    "statistical significance requirement."
                ),
                target_requirement="statistical_significance",
                recommendations=[
                    "Increase statistical power with additional data.",
                    "Repeat the experiment under the same protocol.",
                    "Inspect variance and measurement noise.",
                ],
                notes=(
                    "The selector does not recommend changing results "
                    "to obtain significance. The next action is intended "
                    "to improve evidence quality and statistical power."
                ),
                **common_fields,
            )

        if not robustness_evaluation.is_evaluated:
            return NextExperimentSelection(
                is_selected=True,
                action="test_robustness",
                priority="high",
                reason=(
                    "Robustness evaluation has not been completed."
                ),
                target_requirement="robustness_evaluation",
                recommendations=[
                    "Collect observations suitable for robustness checks.",
                    "Repeat the experiment across comparable conditions.",
                    "Evaluate directional and split-sample consistency.",
                ],
                notes=(
                    "Statistical evidence should be followed by "
                    "robustness diagnostics."
                ),
                **common_fields,
            )

        if not robustness_evaluation.is_robust:
            return NextExperimentSelection(
                is_selected=True,
                action="test_robustness",
                priority="high",
                reason=(
                    "The current evidence does not satisfy the "
                    "robustness requirement."
                ),
                target_requirement="robustness",
                recommendations=[
                    "Replicate the experiment with new observations.",
                    "Test stability across comparable conditions.",
                    "Inspect directional and split-sample instability.",
                ],
                notes=(
                    "The next cycle should test whether the observed "
                    "effect is stable rather than optimize the raw metric."
                ),
                **common_fields,
            )

        if evidence_strength_evaluation.has_contradiction:
            return NextExperimentSelection(
                is_selected=True,
                action="resolve_contradiction",
                priority="critical",
                reason=(
                    "The scientific evaluation pipeline detected a "
                    "contradiction between evidence signals."
                ),
                target_requirement="contradiction_absence",
                recommendations=[
                    "Replicate the conflicting experimental condition.",
                    "Inspect statistical and robustness disagreement.",
                    "Collect independent observations.",
                ],
                notes=(
                    "Contradictory evidence should be resolved before "
                    "the hypothesis decision is treated as stable."
                ),
                **common_fields,
            )

        if not hypothesis_decision.is_evaluated:
            return NextExperimentSelection(
                is_selected=True,
                action="replicate_experiment",
                priority="medium",
                reason=(
                    "The final hypothesis decision could not be "
                    "completed."
                ),
                target_requirement="hypothesis_decision",
                recommendations=[
                    "Replicate the experiment under the same protocol.",
                    "Preserve raw observations and evaluation metadata.",
                    "Re-run the complete scientific pipeline.",
                ],
                notes=(
                    "A replication is recommended because the decision "
                    "layer remains incomplete."
                ),
                **common_fields,
            )

        if failed_requirements:
            return NextExperimentSelection(
                is_selected=True,
                action="replicate_experiment",
                priority="medium",
                reason=(
                    "The hypothesis decision contains unresolved failed "
                    "requirements."
                ),
                target_requirement=failed_requirements[0],
                recommendations=[
                    "Repeat the experiment using the same protocol.",
                    "Target the first unresolved decision requirement.",
                    "Compare the new evidence with the previous cycle.",
                ],
                notes=(
                    "Replication is selected because no earlier "
                    "specialized evidence gap matched the current state."
                ),
                **common_fields,
            )

        if hypothesis_decision.is_supported:
            return NextExperimentSelection(
                is_selected=True,
                action="replicate_experiment",
                priority="low",
                reason=(
                    "The hypothesis is currently supported and the next "
                    "useful action is independent replication."
                ),
                target_requirement="independent_replication",
                recommendations=[
                    "Run an independent replication.",
                    "Use new observations.",
                    "Compare evidence strength across replications.",
                ],
                notes=(
                    "Supported hypotheses still benefit from independent "
                    "replication."
                ),
                **common_fields,
            )

        return NextExperimentSelection(
            is_selected=False,
            action="none",
            priority="low",
            reason=(
                "No specialized next research action was selected from "
                "the current evaluation state."
            ),
            target_requirement=None,
            recommendations=[],
            notes=(
                "The current pipeline state does not match a configured "
                "next-experiment selection rule."
            ),
            **common_fields,
        )