from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.research_recommendation import (
    ResearchRecommendation,
    ResearchRecommendationPriority,
)


SNAPSHOT_FINGERPRINT = "a" * 64


def build_item(
    item_id: str,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=f"Statement {item_id}.",
        confidence=0.85,
        applicability=(
            "liquid markets",
            "trending markets",
        ),
        limitations=(
            "limited history",
        ),
        supporting_findings=(
            f"{item_id}-finding-a",
        ),
        version=1,
        provenance=(
            (
                "source",
                f"{item_id}-source",
            ),
        ),
    )


def build_gap() -> KnowledgeGap:
    return KnowledgeGap(
        gap_type=KnowledgeGapType.ISOLATED_ITEM,
        items=(build_item("knowledge-a"),),
        applicability=(
            "trending markets",
            "liquid markets",
        ),
        reason="Knowledge item is isolated.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )


def build_recommendation(
    *,
    gap: KnowledgeGap | None = None,
    priority: ResearchRecommendationPriority = (
        ResearchRecommendationPriority.MEDIUM
    ),
    question: str = (
        "How does this knowledge relate "
        "to existing findings?"
    ),
    rationale: str = (
        "The isolated knowledge requires "
        "a connecting experiment."
    ),
) -> ResearchRecommendation:
    return ResearchRecommendation(
        gap=gap or build_gap(),
        priority=priority,
        question=question,
        rationale=rationale,
    )


def test_exposes_recommendation_priorities(
) -> None:
    assert tuple(
        priority.value
        for priority
        in ResearchRecommendationPriority
    ) == (
        "low",
        "medium",
        "high",
    )


def test_normalizes_recommendation() -> None:
    gap = build_gap()

    recommendation = build_recommendation(
        gap=gap,
        priority=(
            ResearchRecommendationPriority.HIGH
        ),
        question=(
            "  Which experiment resolves "
            "this gap?  "
        ),
        rationale=(
            "  The conflict blocks reuse.  "
        ),
    )

    assert recommendation.gap is gap
    assert recommendation.priority is (
        ResearchRecommendationPriority.HIGH
    )
    assert recommendation.question == (
        "Which experiment resolves this gap?"
    )
    assert recommendation.rationale == (
        "The conflict blocks reuse."
    )


def test_derives_applicability_from_gap(
) -> None:
    gap = build_gap()

    recommendation = build_recommendation(
        gap=gap
    )

    assert recommendation.applicability == (
        gap.applicability
    )


def test_serializes_full_gap_provenance(
) -> None:
    gap = build_gap()
    recommendation = build_recommendation(
        gap=gap
    )

    assert recommendation.to_dict() == {
        "schema_version": 1,
        "gap": {
            **gap.to_dict(),
            "fingerprint": gap.fingerprint,
        },
        "priority": "medium",
        "question": (
            "How does this knowledge relate "
            "to existing findings?"
        ),
        "rationale": (
            "The isolated knowledge requires "
            "a connecting experiment."
        ),
        "applicability": [
            "liquid markets",
            "trending markets",
        ],
    }


def test_fingerprint_is_deterministic(
) -> None:
    first = build_recommendation()
    second = build_recommendation()

    assert first.fingerprint == (
        second.fingerprint
    )
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_priority(
) -> None:
    medium = build_recommendation()
    high = build_recommendation(
        priority=(
            ResearchRecommendationPriority.HIGH
        )
    )

    assert medium.fingerprint != (
        high.fingerprint
    )


def test_fingerprint_changes_with_question(
) -> None:
    first = build_recommendation()
    second = build_recommendation(
        question=(
            "Which evidence should be "
            "collected next?"
        )
    )

    assert first.fingerprint != (
        second.fingerprint
    )


def test_recommendation_is_immutable(
) -> None:
    recommendation = build_recommendation()

    with pytest.raises(FrozenInstanceError):
        recommendation.question = (  # type: ignore[misc]
            "Changed?"
        )


@pytest.mark.parametrize(
    "gap",
    (
        object(),
        None,
        "gap",
    ),
)
def test_rejects_non_knowledge_gap(
    gap: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="gap must be a KnowledgeGap",
    ):
        ResearchRecommendation(
            gap=gap,  # type: ignore[arg-type]
            priority=(
                ResearchRecommendationPriority
                .MEDIUM
            ),
            question="What should be tested?",
            rationale="A gap was detected.",
        )


@pytest.mark.parametrize(
    "priority",
    (
        "medium",
        None,
        1,
    ),
)
def test_rejects_invalid_priority(
    priority: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "priority must be a "
            "ResearchRecommendationPriority"
        ),
    ):
        ResearchRecommendation(
            gap=build_gap(),
            priority=priority,  # type: ignore[arg-type]
            question="What should be tested?",
            rationale="A gap was detected.",
        )


@pytest.mark.parametrize(
    "question",
    (
        None,
        1,
        True,
    ),
)
def test_rejects_non_string_question(
    question: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="question must be a string",
    ):
        build_recommendation(
            question=question,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "question",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_question(
    question: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="question must not be empty",
    ):
        build_recommendation(
            question=question
        )


@pytest.mark.parametrize(
    "question",
    (
        "Test this statement.",
        "Collect more evidence",
    ),
)
def test_requires_question_mark(
    question: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "question must end with a "
            "question mark"
        ),
    ):
        build_recommendation(
            question=question
        )


@pytest.mark.parametrize(
    "rationale",
    (
        None,
        1,
        True,
    ),
)
def test_rejects_non_string_rationale(
    rationale: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="rationale must be a string",
    ):
        build_recommendation(
            rationale=rationale,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "rationale",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_rationale(
    rationale: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "rationale must not be empty"
        ),
    ):
        build_recommendation(
            rationale=rationale
        )
