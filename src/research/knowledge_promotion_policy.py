from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real

from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)


def _normalize_allowed_states(
    value: object,
) -> tuple[HypothesisEvaluationState, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "allowed_states must be a tuple"
        )

    if not value:
        raise ValueError(
            "allowed_states must not be empty"
        )

    if not all(
        isinstance(
            state,
            HypothesisEvaluationState,
        )
        for state in value
    ):
        raise TypeError(
            "allowed_states must contain only "
            "HypothesisEvaluationState values"
        )

    if len(value) != len(set(value)):
        raise ValueError(
            "allowed_states must not contain duplicates"
        )

    return tuple(
        sorted(
            value,
            key=lambda state: state.value,
        )
    )


def _normalize_minimum_confidence(
    value: object,
) -> float:
    if (
        not isinstance(value, Real)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "minimum_confidence must be a real number"
        )

    normalized = float(value)

    if not isfinite(normalized):
        raise ValueError(
            "minimum_confidence must be finite"
        )

    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            "minimum_confidence must be between 0 and 1"
        )

    return normalized


def _normalize_minimum_findings(
    value: object,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "minimum_findings must be an integer"
        )

    if value < 1:
        raise ValueError(
            "minimum_findings must be positive"
        )

    return value


@dataclass(frozen=True, slots=True)
class KnowledgePromotionPolicy:
    """
    Decides whether a HypothesisEvaluation may be promoted.
    """

    allowed_states: tuple[
        HypothesisEvaluationState,
        ...,
    ]
    minimum_confidence: float
    minimum_findings: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "allowed_states",
            _normalize_allowed_states(
                self.allowed_states
            ),
        )
        object.__setattr__(
            self,
            "minimum_confidence",
            _normalize_minimum_confidence(
                self.minimum_confidence
            ),
        )
        object.__setattr__(
            self,
            "minimum_findings",
            _normalize_minimum_findings(
                self.minimum_findings
            ),
        )

    def allows(
        self,
        *,
        evaluation: HypothesisEvaluation,
    ) -> bool:
        return not self.rejection_reasons(
            evaluation=evaluation
        )

    def rejection_reasons(
        self,
        *,
        evaluation: HypothesisEvaluation,
    ) -> tuple[str, ...]:
        if not isinstance(
            evaluation,
            HypothesisEvaluation,
        ):
            raise TypeError(
                "evaluation must be a "
                "HypothesisEvaluation"
            )

        reasons: list[str] = []

        if evaluation.state not in self.allowed_states:
            allowed = ", ".join(
                state.value
                for state in self.allowed_states
            )
            reasons.append(
                f"state must be one of: {allowed}"
            )

        if (
            evaluation.confidence
            < self.minimum_confidence
        ):
            reasons.append(
                "confidence must be at least "
                f"{self.minimum_confidence!r}"
            )

        if (
            len(evaluation.finding_refs)
            < self.minimum_findings
        ):
            reasons.append(
                "finding_refs must contain at least "
                f"{self.minimum_findings} items"
            )

        return tuple(reasons)
