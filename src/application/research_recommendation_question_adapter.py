from collections.abc import Callable
from datetime import datetime, timezone

from src.research.question import ResearchQuestion
from src.research.research_recommendation import (
    ResearchRecommendation,
)


ResearchQuestionClock = Callable[
    [],
    datetime,
]
ResearchQuestionIdFactory = Callable[
    [ResearchRecommendation],
    str,
]


def _normalize_recommendation(
    value: object,
) -> ResearchRecommendation:
    if not isinstance(
        value,
        ResearchRecommendation,
    ):
        raise TypeError(
            "recommendation must be a "
            "ResearchRecommendation"
        )

    return value


def _normalize_question_id(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "id_factory must return a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "id_factory must return a "
            "non-empty ID"
        )

    return normalized


def _normalize_created_at(
    value: object,
) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(
            "clock must return a datetime"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            "clock must return a "
            "timezone-aware datetime"
        )

    return value.astimezone(timezone.utc)


class ResearchRecommendationQuestionAdapter:
    """
    Adapts a recommendation to the legacy ResearchQuestion model.
    """

    def __init__(
        self,
        *,
        clock: ResearchQuestionClock,
        id_factory: ResearchQuestionIdFactory,
    ) -> None:
        if not callable(clock):
            raise TypeError(
                "clock must be callable"
            )

        if not callable(id_factory):
            raise TypeError(
                "id_factory must be callable"
            )

        self._clock = clock
        self._id_factory = id_factory

    def adapt(
        self,
        recommendation: ResearchRecommendation,
    ) -> ResearchQuestion:
        normalized_recommendation = (
            _normalize_recommendation(
                recommendation
            )
        )
        question_id = _normalize_question_id(
            self._id_factory(
                normalized_recommendation
            )
        )
        created_at = _normalize_created_at(
            self._clock()
        )
        description = (
            "Recommendation rationale: "
            f"{normalized_recommendation.rationale}\n"
            "Priority: "
            f"{normalized_recommendation.priority.value}\n"
            "Applicability: "
            + ", ".join(
                normalized_recommendation
                .applicability
            )
            + "\nKnowledge gap fingerprint: "
            + (
                normalized_recommendation
                .gap.fingerprint
            )
            + "\nRecommendation fingerprint: "
            + normalized_recommendation.fingerprint
        )

        return ResearchQuestion(
            id=question_id,
            statement=(
                normalized_recommendation
                .question
            ),
            description=description,
            created_at=created_at,
        )
