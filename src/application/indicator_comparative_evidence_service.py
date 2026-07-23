from __future__ import annotations

from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.research.comparative_evidence_evaluator import (
    ComparativeEvidenceEvaluator,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.evidence import Evidence


class IndicatorComparativeEvidenceService:
    """
    Builds Evidence from compatible comparative research results.

    This application service selects one statistical horizon and
    delegates all scientific classification rules to the domain
    ComparativeEvidenceEvaluator.
    """

    def __init__(
        self,
        *,
        evidence_evaluator: ComparativeEvidenceEvaluator,
    ) -> None:
        if not isinstance(
            evidence_evaluator,
            ComparativeEvidenceEvaluator,
        ):
            raise TypeError(
                "evidence_evaluator must be a "
                "ComparativeEvidenceEvaluator"
            )

        self._evidence_evaluator = (
            evidence_evaluator
        )

    def evaluate(
        self,
        *,
        hypothesis_id: str,
        results: tuple[
            IndicatorComparativeResearchResult,
            ...,
        ],
        horizon: int,
    ) -> Evidence:
        normalized_horizon = (
            self._validate_horizon(horizon)
        )
        normalized_results = (
            self._validate_results(results)
        )
        reference = normalized_results[0]

        evaluations = tuple(
            self._select_evaluation(
                result,
                horizon=normalized_horizon,
            )
            for result in normalized_results
        )

        return self._evidence_evaluator.evaluate(
            hypothesis_id=hypothesis_id,
            indicator_id=reference.indicator_id,
            symbol=reference.symbol,
            timeframe=reference.timeframe,
            evaluations=evaluations,
            plan=reference.evaluation_plan,
        )

    @classmethod
    def _validate_results(
        cls,
        results: object,
    ) -> tuple[
        IndicatorComparativeResearchResult,
        ...,
    ]:
        if not isinstance(results, tuple):
            raise TypeError(
                "results must be a tuple"
            )

        if not results:
            raise ValueError(
                "results must not be empty"
            )

        normalized: list[
            IndicatorComparativeResearchResult
        ] = []

        for result in results:
            if not isinstance(
                result,
                IndicatorComparativeResearchResult,
            ):
                raise TypeError(
                    "each result must be an "
                    "IndicatorComparativeResearchResult"
                )

            normalized.append(result)

        dataset_ids = tuple(
            result.dataset_id
            for result in normalized
        )

        if len(dataset_ids) != len(set(dataset_ids)):
            raise ValueError(
                "results must use distinct datasets"
            )

        ordered = tuple(
            sorted(
                normalized,
                key=lambda result: result.dataset_id,
            )
        )
        reference = ordered[0]

        for result in ordered[1:]:
            cls._validate_compatibility(
                reference,
                result,
            )

        return ordered

    @staticmethod
    def _validate_compatibility(
        reference: IndicatorComparativeResearchResult,
        result: IndicatorComparativeResearchResult,
    ) -> None:
        if result.indicator_id != reference.indicator_id:
            raise ValueError(
                "results must use the same indicator"
            )

        if result.symbol != reference.symbol:
            raise ValueError(
                "results must use the same symbol"
            )

        if result.timeframe != reference.timeframe:
            raise ValueError(
                "results must use the same timeframe"
            )

        if (
            result.research_fingerprint
            != reference.research_fingerprint
        ):
            raise ValueError(
                "results must use the same "
                "research fingerprint"
            )

        if (
            result.evaluation_plan_fingerprint
            != reference.evaluation_plan_fingerprint
        ):
            raise ValueError(
                "results must use the same "
                "evaluation plan"
            )

    @staticmethod
    def _select_evaluation(
        result: IndicatorComparativeResearchResult,
        *,
        horizon: int,
    ) -> ComparativeStatisticalEvaluation:
        for evaluation in (
            result.statistical_evaluations
        ):
            if evaluation.horizon == horizon:
                return evaluation

        raise ValueError(
            f"result dataset '{result.dataset_id}' "
            f"does not contain horizon {horizon}"
        )

    @staticmethod
    def _validate_horizon(
        value: object,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "horizon must be an integer"
            )

        if value < 1:
            raise ValueError(
                "horizon must be positive"
            )

        return value
