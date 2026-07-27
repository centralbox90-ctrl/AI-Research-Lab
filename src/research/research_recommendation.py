from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256

from src.research.knowledge_gap import KnowledgeGap


class ResearchRecommendationPriority(
    str,
    Enum,
):
    """Supported priorities for future research."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _normalize_gap(
    value: object,
) -> KnowledgeGap:
    if not isinstance(value, KnowledgeGap):
        raise TypeError(
            "gap must be a KnowledgeGap"
        )

    return value


def _normalize_priority(
    value: object,
) -> ResearchRecommendationPriority:
    if not isinstance(
        value,
        ResearchRecommendationPriority,
    ):
        raise TypeError(
            "priority must be a "
            "ResearchRecommendationPriority"
        )

    return value


def _normalize_question(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "question must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "question must not be empty"
        )

    if not normalized.endswith("?"):
        raise ValueError(
            "question must end with a "
            "question mark"
        )

    return normalized


def _normalize_rationale(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "rationale must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "rationale must not be empty"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class ResearchRecommendation:
    """
    Immutable recommendation grounded in an exact knowledge gap.
    """

    gap: KnowledgeGap
    priority: ResearchRecommendationPriority
    question: str
    rationale: str
    applicability: tuple[str, ...] = field(
        init=False
    )

    def __post_init__(self) -> None:
        gap = _normalize_gap(self.gap)
        priority = _normalize_priority(
            self.priority
        )
        question = _normalize_question(
            self.question
        )
        rationale = _normalize_rationale(
            self.rationale
        )

        object.__setattr__(
            self,
            "gap",
            gap,
        )
        object.__setattr__(
            self,
            "priority",
            priority,
        )
        object.__setattr__(
            self,
            "question",
            question,
        )
        object.__setattr__(
            self,
            "rationale",
            rationale,
        )
        object.__setattr__(
            self,
            "applicability",
            gap.applicability,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "gap": {
                **self.gap.to_dict(),
                "fingerprint": (
                    self.gap.fingerprint
                ),
            },
            "priority": self.priority.value,
            "question": self.question,
            "rationale": self.rationale,
            "applicability": list(
                self.applicability
            ),
        }

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()
