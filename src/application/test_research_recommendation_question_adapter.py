from datetime import datetime, timedelta, timezone

import pytest

from src.application.research_recommendation_question_adapter import (
    ResearchRecommendationQuestionAdapter,
)
from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.research_recommendation import (
    ResearchRecommendation,
    ResearchRecommendationPriority,
)
from src.research.research_types import ResearchStatus


def build_recommendation() -> (
    ResearchRecommendation
):
    item = KnowledgeItem(
        id="knowledge-a",
        statement="Momentum persists.",
        confidence=0.85,
        applicability=(
            "liquid markets",
        ),
        limitations=(
            "limited history",
        ),
        supporting_findings=(
            "finding-a",
        ),
        version=1,
        provenance=(
            (
                "source",
                "experiment-a",
            ),
        ),
    )
    gap = KnowledgeGap(
        gap_type=(
            KnowledgeGapType.UNSUPPORTED_ITEM
        ),
        items=(item,),
        applicability=(
            "liquid markets",
        ),
        reason="Support is missing.",
        snapshot_fingerprint="a" * 64,
    )

    return ResearchRecommendation(
        gap=gap,
        priority=(
            ResearchRecommendationPriority.MEDIUM
        ),
        question=(
            "What independent evidence "
            "supports momentum persistence?"
        ),
        rationale=(
            "Independent confirmation is "
            "required."
        ),
    )


def test_adapts_recommendation_to_question(
) -> None:
    recommendation = build_recommendation()
    created_at = datetime(
        2026,
        7,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: created_at,
            id_factory=(
                lambda value: (
                    "question-"
                    + value.fingerprint[:12]
                )
            ),
        )
    )

    question = adapter.adapt(
        recommendation
    )

    assert question.id == (
        "question-"
        + recommendation.fingerprint[:12]
    )
    assert question.statement == (
        recommendation.question
    )
    assert question.created_at == created_at
    assert question.status is ResearchStatus.NEW
    assert question.description == (
        "Recommendation rationale: "
        "Independent confirmation is "
        "required.\n"
        "Priority: medium\n"
        "Applicability: liquid markets\n"
        "Knowledge gap fingerprint: "
        f"{recommendation.gap.fingerprint}\n"
        "Recommendation fingerprint: "
        f"{recommendation.fingerprint}"
    )


def test_converts_created_at_to_utc(
) -> None:
    local_timezone = timezone(
        timedelta(hours=3)
    )
    local_time = datetime(
        2026,
        7,
        27,
        15,
        30,
        tzinfo=local_timezone,
    )
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: local_time,
            id_factory=lambda _: "question-a",
        )
    )

    question = adapter.adapt(
        build_recommendation()
    )

    assert question.created_at == datetime(
        2026,
        7,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )
    assert question.created_at.tzinfo is (
        timezone.utc
    )


def test_passes_recommendation_to_id_factory(
) -> None:
    recommendation = build_recommendation()
    received: list[
        ResearchRecommendation
    ] = []

    def id_factory(
        value: ResearchRecommendation,
    ) -> str:
        received.append(value)
        return "question-a"

    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: datetime(
                2026,
                7,
                27,
                tzinfo=timezone.utc,
            ),
            id_factory=id_factory,
        )
    )

    adapter.adapt(recommendation)

    assert received == [recommendation]


def test_calls_each_dependency_once(
) -> None:
    clock_calls = 0
    id_calls = 0

    def clock() -> datetime:
        nonlocal clock_calls
        clock_calls += 1
        return datetime(
            2026,
            7,
            27,
            tzinfo=timezone.utc,
        )

    def id_factory(
        _: ResearchRecommendation,
    ) -> str:
        nonlocal id_calls
        id_calls += 1
        return "question-a"

    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=clock,
            id_factory=id_factory,
        )
    )

    adapter.adapt(build_recommendation())

    assert clock_calls == 1
    assert id_calls == 1


def test_is_deterministic_for_injected_values(
) -> None:
    created_at = datetime(
        2026,
        7,
        27,
        tzinfo=timezone.utc,
    )
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: created_at,
            id_factory=lambda _: "question-a",
        )
    )
    recommendation = build_recommendation()

    first = adapter.adapt(recommendation)
    second = adapter.adapt(recommendation)

    assert first == second
    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize(
    ("field_name", "clock", "id_factory"),
    (
        (
            "clock",
            None,
            lambda _: "question-a",
        ),
        (
            "clock",
            object(),
            lambda _: "question-a",
        ),
        (
            "id_factory",
            lambda: datetime.now(
                timezone.utc
            ),
            None,
        ),
        (
            "id_factory",
            lambda: datetime.now(
                timezone.utc
            ),
            object(),
        ),
    ),
)
def test_requires_callable_dependencies(
    field_name: str,
    clock: object,
    id_factory: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be callable"
        ),
    ):
        ResearchRecommendationQuestionAdapter(
            clock=clock,  # type: ignore[arg-type]
            id_factory=id_factory,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "recommendation",
    (
        object(),
        None,
        "recommendation",
    ),
)
def test_rejects_non_recommendation(
    recommendation: object,
) -> None:
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: datetime(
                2026,
                7,
                27,
                tzinfo=timezone.utc,
            ),
            id_factory=lambda _: "question-a",
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "recommendation must be a "
            "ResearchRecommendation"
        ),
    ):
        adapter.adapt(
            recommendation,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "question_id",
    (
        None,
        1,
        True,
    ),
)
def test_rejects_non_string_id(
    question_id: object,
) -> None:
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: datetime(
                2026,
                7,
                27,
                tzinfo=timezone.utc,
            ),
            id_factory=(  # type: ignore[arg-type]
                lambda _: question_id
            ),
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "id_factory must return a string"
        ),
    ):
        adapter.adapt(build_recommendation())


@pytest.mark.parametrize(
    "question_id",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_id(
    question_id: str,
) -> None:
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: datetime(
                2026,
                7,
                27,
                tzinfo=timezone.utc,
            ),
            id_factory=lambda _: question_id,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "id_factory must return a "
            "non-empty ID"
        ),
    ):
        adapter.adapt(build_recommendation())


@pytest.mark.parametrize(
    "created_at",
    (
        None,
        "2026-07-27",
        1,
    ),
)
def test_rejects_non_datetime_clock_value(
    created_at: object,
) -> None:
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=(  # type: ignore[arg-type]
                lambda: created_at
            ),
            id_factory=lambda _: "question-a",
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "clock must return a datetime"
        ),
    ):
        adapter.adapt(build_recommendation())


def test_rejects_naive_datetime(
) -> None:
    adapter = (
        ResearchRecommendationQuestionAdapter(
            clock=lambda: datetime(
                2026,
                7,
                27,
            ),
            id_factory=lambda _: "question-a",
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "clock must return a "
            "timezone-aware datetime"
        ),
    ):
        adapter.adapt(build_recommendation())
