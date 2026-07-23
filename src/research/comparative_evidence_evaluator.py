from __future__ import annotations

import json
from hashlib import sha256
from math import isclose

from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
    ExpectedEffectDirection,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)


class ComparativeEvidenceEvaluator:
    """
    Converts replicated statistical evaluations into Evidence.

    The evaluator applies only rules declared by the evaluation plan.
    It does not create a Finding or change the hypothesis.
    """

    def evaluate(
        self,
        *,
        hypothesis_id: str,
        indicator_id: str,
        symbol: str,
        timeframe: str,
        evaluations: tuple[
            ComparativeStatisticalEvaluation,
            ...,
        ],
        plan: ComparativeEvaluationPlan,
    ) -> Evidence:
        normalized_hypothesis_id = self._normalize_text(
            hypothesis_id,
            field_name="hypothesis_id",
        )
        normalized_indicator_id = self._normalize_text(
            indicator_id,
            field_name="indicator_id",
        )
        normalized_symbol = self._normalize_text(
            symbol,
            field_name="symbol",
        ).upper()
        normalized_timeframe = self._normalize_text(
            timeframe,
            field_name="timeframe",
        ).upper()

        if not isinstance(
            plan,
            ComparativeEvaluationPlan,
        ):
            raise TypeError(
                "plan must be a ComparativeEvaluationPlan"
            )

        normalized_evaluations = (
            self._validate_evaluations(
                evaluations,
                plan=plan,
            )
        )
        horizon = normalized_evaluations[0].horizon
        research_fingerprint = (
            normalized_evaluations[0]
            .research_fingerprint
        )

        eligible_evaluations = tuple(
            evaluation
            for evaluation in normalized_evaluations
            if (
                evaluation.candidate_sample_size
                >= plan.minimum_candidate_sample_size
            )
        )

        supporting_count = 0
        contradictory_count = 0

        for evaluation in eligible_evaluations:
            supporting, contradictory = (
                self._classify_interval(
                    evaluation,
                    expected_direction=(
                        plan.expected_direction
                    ),
                )
            )

            if supporting:
                supporting_count += 1

            if contradictory:
                contradictory_count += 1

        direction = self._resolve_direction(
            eligible_count=len(
                eligible_evaluations
            ),
            supporting_count=supporting_count,
            contradictory_count=(
                contradictory_count
            ),
            plan=plan,
        )
        strength = self._resolve_strength(
            direction=direction,
            eligible_count=len(
                eligible_evaluations
            ),
            supporting_count=supporting_count,
            contradictory_count=(
                contradictory_count
            ),
            plan=plan,
        )
        confidence = self._calculate_confidence(
            direction=direction,
            eligible_count=len(
                eligible_evaluations
            ),
            supporting_count=supporting_count,
            contradictory_count=(
                contradictory_count
            ),
            confidence_level=(
                plan.confidence_level
            ),
        )
        consistency = self._calculate_consistency(
            eligible_evaluations,
            expected_direction=(
                plan.expected_direction
            ),
        )
        robustness = (
            len(eligible_evaluations)
            / len(normalized_evaluations)
        )
        limitations = self._build_limitations(
            evaluations=normalized_evaluations,
            eligible_count=len(
                eligible_evaluations
            ),
            supporting_count=supporting_count,
            contradictory_count=(
                contradictory_count
            ),
            plan=plan,
        )
        dataset_ids = tuple(
            evaluation.dataset_id
            for evaluation in normalized_evaluations
        )
        observation_refs = tuple(
            (
                f"{dataset_id}:"
                f"horizon:{horizon}"
            )
            for dataset_id in dataset_ids
        )
        evidence_id = self._build_evidence_id(
            hypothesis_id=(
                normalized_hypothesis_id
            ),
            indicator_id=(
                normalized_indicator_id
            ),
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            horizon=horizon,
            research_fingerprint=(
                research_fingerprint
            ),
            evaluation_plan_fingerprint=(
                plan.fingerprint
            ),
            dataset_ids=dataset_ids,
        )

        return Evidence(
            id=evidence_id,
            hypothesis_id=(
                normalized_hypothesis_id
            ),
            observation_refs=observation_refs,
            direction=direction,
            strength=strength,
            confidence=confidence,
            consistency=consistency,
            robustness=robustness,
            provenance=(
                (
                    "research_fingerprint",
                    research_fingerprint,
                ),
                (
                    "evaluation_plan_fingerprint",
                    plan.fingerprint,
                ),
                (
                    "horizon",
                    str(horizon),
                ),
                (
                    "replication_count",
                    str(
                        len(normalized_evaluations)
                    ),
                ),
                (
                    "eligible_replication_count",
                    str(
                        len(eligible_evaluations)
                    ),
                ),
                (
                    "supporting_replication_count",
                    str(supporting_count),
                ),
                (
                    "contradictory_replication_count",
                    str(contradictory_count),
                ),
                (
                    "dataset_ids",
                    json.dumps(
                        dataset_ids,
                        separators=(",", ":"),
                    ),
                ),
            ),
            applicability=(
                (
                    "indicator:"
                    f"{normalized_indicator_id}"
                ),
                f"symbol:{normalized_symbol}",
                f"timeframe:{normalized_timeframe}",
                f"horizon:{horizon}",
            ),
            limitations=limitations,
        )

    @classmethod
    def _validate_evaluations(
        cls,
        evaluations: object,
        *,
        plan: ComparativeEvaluationPlan,
    ) -> tuple[
        ComparativeStatisticalEvaluation,
        ...,
    ]:
        if not isinstance(evaluations, tuple):
            raise TypeError(
                "evaluations must be a tuple"
            )

        if not evaluations:
            raise ValueError(
                "evaluations must not be empty"
            )

        normalized: list[
            ComparativeStatisticalEvaluation
        ] = []

        for evaluation in evaluations:
            if not isinstance(
                evaluation,
                ComparativeStatisticalEvaluation,
            ):
                raise TypeError(
                    "each evaluation must be a "
                    "ComparativeStatisticalEvaluation"
                )

            cls._validate_evaluation_plan(
                evaluation,
                plan=plan,
            )
            normalized.append(evaluation)

        research_fingerprints = {
            evaluation.research_fingerprint
            for evaluation in normalized
        }

        if len(research_fingerprints) != 1:
            raise ValueError(
                "evaluations must use the same "
                "research fingerprint"
            )

        horizons = {
            evaluation.horizon
            for evaluation in normalized
        }

        if len(horizons) != 1:
            raise ValueError(
                "evaluations must use the same horizon"
            )

        dataset_ids = tuple(
            evaluation.dataset_id
            for evaluation in normalized
        )

        if len(dataset_ids) != len(set(dataset_ids)):
            raise ValueError(
                "evaluations must use distinct datasets"
            )

        return tuple(
            sorted(
                normalized,
                key=lambda evaluation: (
                    evaluation.dataset_id
                ),
            )
        )

    @staticmethod
    def _validate_evaluation_plan(
        evaluation: ComparativeStatisticalEvaluation,
        *,
        plan: ComparativeEvaluationPlan,
    ) -> None:
        if evaluation.method != plan.method:
            raise ValueError(
                "evaluation method must match the plan"
            )

        if not isclose(
            evaluation.confidence_level,
            plan.confidence_level,
            rel_tol=1e-12,
            abs_tol=1e-15,
        ):
            raise ValueError(
                "evaluation confidence level must "
                "match the plan"
            )

        if (
            evaluation.resample_count
            != plan.resample_count
        ):
            raise ValueError(
                "evaluation resample count must "
                "match the plan"
            )

        if (
            evaluation.block_length
            != plan.block_length
        ):
            raise ValueError(
                "evaluation block length must "
                "match the plan"
            )

        if (
            evaluation.random_seed
            != plan.random_seed
        ):
            raise ValueError(
                "evaluation random seed must "
                "match the plan"
            )

    @staticmethod
    def _classify_interval(
        evaluation: ComparativeStatisticalEvaluation,
        *,
        expected_direction: ExpectedEffectDirection,
    ) -> tuple[bool, bool]:
        if (
            expected_direction
            is ExpectedEffectDirection.POSITIVE
        ):
            return (
                (
                    evaluation
                    .confidence_interval_lower
                    > 0.0
                ),
                (
                    evaluation
                    .confidence_interval_upper
                    < 0.0
                ),
            )

        if (
            expected_direction
            is ExpectedEffectDirection.NEGATIVE
        ):
            return (
                (
                    evaluation
                    .confidence_interval_upper
                    < 0.0
                ),
                (
                    evaluation
                    .confidence_interval_lower
                    > 0.0
                ),
            )

        return (
            evaluation.excludes_zero,
            False,
        )

    @staticmethod
    def _resolve_direction(
        *,
        eligible_count: int,
        supporting_count: int,
        contradictory_count: int,
        plan: ComparativeEvaluationPlan,
    ) -> EvidenceDirection:
        if contradictory_count > 0:
            return EvidenceDirection.CONTRADICTORY

        enough_replications = (
            eligible_count
            >= plan.minimum_replication_count
        )
        enough_supporting = (
            supporting_count
            >= (
                plan
                .minimum_supporting_replication_count
            )
        )

        if enough_replications and enough_supporting:
            return EvidenceDirection.SUPPORTING

        return EvidenceDirection.INCONCLUSIVE

    @staticmethod
    def _resolve_strength(
        *,
        direction: EvidenceDirection,
        eligible_count: int,
        supporting_count: int,
        contradictory_count: int,
        plan: ComparativeEvaluationPlan,
    ) -> EvidenceStrength:
        if direction is EvidenceDirection.SUPPORTING:
            if (
                eligible_count
                >= plan.minimum_replication_count
                and supporting_count
                == eligible_count
            ):
                return EvidenceStrength.STRONG

            return EvidenceStrength.MODERATE

        if (
            direction
            is EvidenceDirection.CONTRADICTORY
        ):
            if (
                eligible_count
                >= plan.minimum_replication_count
                and contradictory_count
                == eligible_count
            ):
                return EvidenceStrength.STRONG

            return EvidenceStrength.MODERATE

        if (
            supporting_count > 0
            or contradictory_count > 0
        ):
            return EvidenceStrength.WEAK

        return EvidenceStrength.NONE

    @staticmethod
    def _calculate_confidence(
        *,
        direction: EvidenceDirection,
        eligible_count: int,
        supporting_count: int,
        contradictory_count: int,
        confidence_level: float,
    ) -> float:
        if eligible_count == 0:
            return 0.0

        if direction is EvidenceDirection.SUPPORTING:
            decisive_count = supporting_count
        elif (
            direction
            is EvidenceDirection.CONTRADICTORY
        ):
            decisive_count = contradictory_count
        else:
            decisive_count = max(
                supporting_count,
                contradictory_count,
            )

        return (
            decisive_count
            / eligible_count
            * confidence_level
        )

    @staticmethod
    def _calculate_consistency(
        evaluations: tuple[
            ComparativeStatisticalEvaluation,
            ...,
        ],
        *,
        expected_direction: ExpectedEffectDirection,
    ) -> float:
        if not evaluations:
            return 0.0

        positive_count = sum(
            evaluation.effect_estimate > 0.0
            for evaluation in evaluations
        )
        negative_count = sum(
            evaluation.effect_estimate < 0.0
            for evaluation in evaluations
        )

        if (
            expected_direction
            is ExpectedEffectDirection.POSITIVE
        ):
            aligned_count = positive_count
        elif (
            expected_direction
            is ExpectedEffectDirection.NEGATIVE
        ):
            aligned_count = negative_count
        else:
            aligned_count = max(
                positive_count,
                negative_count,
            )

        return aligned_count / len(evaluations)

    @staticmethod
    def _build_limitations(
        *,
        evaluations: tuple[
            ComparativeStatisticalEvaluation,
            ...,
        ],
        eligible_count: int,
        supporting_count: int,
        contradictory_count: int,
        plan: ComparativeEvaluationPlan,
    ) -> tuple[str, ...]:
        limitations: list[str] = []

        if (
            eligible_count
            < plan.minimum_replication_count
        ):
            limitations.append(
                "eligible replication count is below "
                f"{plan.minimum_replication_count}"
            )

        if (
            supporting_count
            < (
                plan
                .minimum_supporting_replication_count
            )
        ):
            limitations.append(
                "supporting replication count is below "
                f"{plan.minimum_supporting_replication_count}"
            )

        ineligible_count = (
            len(evaluations) - eligible_count
        )

        if ineligible_count:
            limitations.append(
                f"{ineligible_count} replication(s) are "
                "below the minimum candidate sample size"
            )

        inconclusive_count = (
            eligible_count
            - supporting_count
            - contradictory_count
        )

        if inconclusive_count:
            limitations.append(
                f"{inconclusive_count} eligible "
                "replication(s) have confidence "
                "intervals including zero"
            )

        if contradictory_count:
            limitations.append(
                f"{contradictory_count} statistically "
                "significant contradictory "
                "replication(s)"
            )

        for evaluation in evaluations:
            for warning in evaluation.warnings:
                limitations.append(
                    f"{evaluation.dataset_id}: {warning}"
                )

        return tuple(
            dict.fromkeys(limitations)
        )

    @staticmethod
    def _build_evidence_id(
        *,
        hypothesis_id: str,
        indicator_id: str,
        symbol: str,
        timeframe: str,
        horizon: int,
        research_fingerprint: str,
        evaluation_plan_fingerprint: str,
        dataset_ids: tuple[str, ...],
    ) -> str:
        payload = {
            "schema_version": 1,
            "hypothesis_id": hypothesis_id,
            "indicator_id": indicator_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon": horizon,
            "research_fingerprint": (
                research_fingerprint
            ),
            "evaluation_plan_fingerprint": (
                evaluation_plan_fingerprint
            ),
            "dataset_ids": dataset_ids,
        }
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        digest = sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return f"evidence:sha256:{digest}"

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized
