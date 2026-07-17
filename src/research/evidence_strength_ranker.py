from collections.abc import Sequence

from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.experiment import Experiment
from src.research.ranked_evidence import RankedEvidence


class EvidenceStrengthRanker:
    """
    Ранжирует эксперименты по рассчитанной силе evidence.

    Ranker не выполняет статистические расчёты и не принимает
    решение о поддержке гипотезы.

    Завершённые evidence evaluations располагаются выше incomplete
    evaluations. Внутри каждой группы используется evidence score.
    """

    def rank(
        self,
        experiments: Sequence[Experiment],
        evaluations: Sequence[EvidenceStrengthEvaluation],
    ) -> list[RankedEvidence]:
        if len(experiments) != len(evaluations):
            raise ValueError(
                "Experiments and evidence evaluations must have "
                "the same length"
            )

        ranked_items: list[RankedEvidence] = []

        for experiment, evaluation in zip(
            experiments,
            evaluations,
            strict=True,
        ):
            warnings = list(evaluation.warnings)

            if (
                evaluation.experiment_id
                and evaluation.experiment_id != experiment.id
            ):
                warnings.append(
                    "Evidence evaluation belongs to a different "
                    "experiment"
                )

            ranked_items.append(
                RankedEvidence(
                    experiment=experiment,
                    evidence_strength_evaluation=evaluation,
                    score=evaluation.score,
                    level=evaluation.level,
                    warnings=warnings,
                )
            )

        ranked_items.sort(
            key=lambda item: (
                (
                    item.evidence_strength_evaluation.is_evaluated
                    if item.evidence_strength_evaluation is not None
                    else False
                ),
                item.score,
            ),
            reverse=True,
        )

        for rank, item in enumerate(ranked_items, start=1):
            item.rank = rank

        return ranked_items

    def best(
        self,
        experiments: Sequence[Experiment],
        evaluations: Sequence[EvidenceStrengthEvaluation],
    ) -> RankedEvidence:
        ranked_items = self.rank(
            experiments=experiments,
            evaluations=evaluations,
        )

        if not ranked_items:
            raise ValueError(
                "At least one experiment and evidence evaluation "
                "are required"
            )

        return ranked_items[0]