from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real

from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)
from src.research.knowledge_item import KnowledgeItem


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


def _normalize_minimum_supporting_findings(
    value: object,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "minimum_supporting_findings must be "
            "an integer"
        )

    if value < 1:
        raise ValueError(
            "minimum_supporting_findings must be "
            "positive"
        )

    return value


class KnowledgeCandidateValidationError(
    ValueError
):
    """Raised when a candidate does not satisfy the policy."""

    def __init__(
        self,
        *,
        candidate_id: str,
        reasons: tuple[str, ...],
    ) -> None:
        self.candidate_id = candidate_id
        self.reasons = reasons

        super().__init__(
            f"knowledge candidate {candidate_id!r} "
            f"was rejected: {'; '.join(reasons)}"
        )


@dataclass(frozen=True, slots=True)
class KnowledgeCandidateValidator:
    """
    Validates a candidate and admits it as initial Knowledge.
    """

    minimum_confidence: float
    minimum_supporting_findings: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "minimum_confidence",
            _normalize_minimum_confidence(
                self.minimum_confidence
            ),
        )
        object.__setattr__(
            self,
            "minimum_supporting_findings",
            _normalize_minimum_supporting_findings(
                self.minimum_supporting_findings
            ),
        )

    def validate(
        self,
        *,
        candidate: KnowledgeCandidate,
    ) -> KnowledgeItem:
        if not isinstance(
            candidate,
            KnowledgeCandidate,
        ):
            raise TypeError(
                "candidate must be a KnowledgeCandidate"
            )

        reasons = self._rejection_reasons(
            candidate
        )

        if reasons:
            raise KnowledgeCandidateValidationError(
                candidate_id=candidate.id,
                reasons=reasons,
            )

        provenance = dict(candidate.provenance)
        provenance.update(
            {
                "hypothesis_evaluation_ref": (
                    candidate
                    .hypothesis_evaluation_ref
                ),
                "knowledge_candidate_fingerprint": (
                    candidate.fingerprint
                ),
                "knowledge_candidate_id": (
                    candidate.id
                ),
                "knowledge_validation_minimum_confidence": (
                    repr(self.minimum_confidence)
                ),
                "knowledge_validation_minimum_supporting_findings": (
                    str(
                        self
                        .minimum_supporting_findings
                    )
                ),
                "knowledge_validation_policy_version": (
                    "1"
                ),
            }
        )

        return KnowledgeItem(
            id=candidate.id,
            statement=candidate.statement,
            confidence=candidate.confidence,
            applicability=candidate.applicability,
            limitations=candidate.limitations,
            supporting_findings=(
                candidate.supporting_findings
            ),
            version=1,
            provenance=tuple(
                provenance.items()
            ),
        )

    def _rejection_reasons(
        self,
        candidate: KnowledgeCandidate,
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if (
            candidate.confidence
            < self.minimum_confidence
        ):
            reasons.append(
                "confidence must be at least "
                f"{self.minimum_confidence!r}"
            )

        if (
            len(candidate.supporting_findings)
            < self.minimum_supporting_findings
        ):
            reasons.append(
                "supporting_findings must contain "
                "at least "
                f"{self.minimum_supporting_findings} "
                "items"
            )

        return tuple(reasons)
