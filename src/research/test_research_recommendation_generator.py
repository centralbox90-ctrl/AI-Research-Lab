import pytest

from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.research_recommendation import (
    ResearchRecommendationPriority,
)
from src.research.research_recommendation_generator import (
    ResearchRecommendationGenerator,
)


SNAPSHOT_FINGERPRINT = "a" * 64


def build_item(
    item_id: str,
    *,
    statement: str | None = None,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=(
            statement
            or f"Statement {item_id}."
        ),
        confidence=0.85,
        applicability=(
            "liquid markets",
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


def build_single_item_gap(
    gap_type: KnowledgeGapType,
    *,
    item_id: str = "knowledge-a",
    statement: str | None = None,
) -> KnowledgeGap:
    return KnowledgeGap(
        gap_type=gap_type,
        items=(
            build_item(
                item_id,
                statement=statement,
            ),
        ),
        applicability=(
            "liquid markets",
        ),
        reason="Explicit topology gap.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )


def build_contradiction_gap(
) -> KnowledgeGap:
    return KnowledgeGap(
        gap_type=(
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
        items=(
            build_item(
                "knowledge-b",
                statement=(
                    "Momentum does not persist."
                ),
            ),
            build_item(
                "knowledge-a",
                statement="Momentum persists.",
            ),
        ),
        applicability=(
            "liquid markets",
        ),
        reason="Conflict is unresolved.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )


def test_generates_isolated_item_recommendation(
) -> None:
    gap = build_single_item_gap(
        KnowledgeGapType.ISOLATED_ITEM,
        statement="Momentum persists.",
    )

    recommendation = (
        ResearchRecommendationGenerator()
        .generate(gap)
    )

    assert recommendation.gap is gap
    assert recommendation.priority is (
        ResearchRecommendationPriority.LOW
    )
    assert recommendation.question == (
        'How can "Momentum persists." '
        "be connected to existing knowledge?"
    )
    assert recommendation.rationale == (
        "The knowledge item has no graph "
        "relations in the referenced snapshot."
    )


def test_generates_unsupported_item_recommendation(
) -> None:
    gap = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM,
        statement="Momentum persists.",
    )

    recommendation = (
        ResearchRecommendationGenerator()
        .generate(gap)
    )

    assert recommendation.priority is (
        ResearchRecommendationPriority.MEDIUM
    )
    assert recommendation.question == (
        "What independent evidence supports "
        '"Momentum persists."?'
    )
    assert recommendation.rationale == (
        "The knowledge item lacks active "
        "incoming supports and outgoing "
        "derived_from relations."
    )


def test_generates_contradiction_recommendation(
) -> None:
    gap = build_contradiction_gap()

    recommendation = (
        ResearchRecommendationGenerator()
        .generate(gap)
    )

    assert recommendation.priority is (
        ResearchRecommendationPriority.HIGH
    )
    assert recommendation.question == (
        "Under which conditions can "
        '"Momentum persists." and '
        '"Momentum does not persist." '
        "be reconciled?"
    )
    assert recommendation.rationale == (
        "The active knowledge items contradict "
        "each other within overlapping "
        "applicability."
    )


@pytest.mark.parametrize(
    ("gap_type", "expected_priority"),
    (
        (
            KnowledgeGapType.ISOLATED_ITEM,
            ResearchRecommendationPriority.LOW,
        ),
        (
            KnowledgeGapType.UNSUPPORTED_ITEM,
            (
                ResearchRecommendationPriority
                .MEDIUM
            ),
        ),
    ),
)
def test_single_item_priority_mapping(
    gap_type: KnowledgeGapType,
    expected_priority: (
        ResearchRecommendationPriority
    ),
) -> None:
    recommendation = (
        ResearchRecommendationGenerator()
        .generate(
            build_single_item_gap(
                gap_type
            )
        )
    )

    assert recommendation.priority is (
        expected_priority
    )


def test_generation_is_deterministic(
) -> None:
    first_gap = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM
    )
    second_gap = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM
    )
    generator = (
        ResearchRecommendationGenerator()
    )

    first = generator.generate(first_gap)
    second = generator.generate(second_gap)

    assert first == second
    assert first.fingerprint == (
        second.fingerprint
    )


def test_generates_all_in_priority_order(
) -> None:
    low = build_single_item_gap(
        KnowledgeGapType.ISOLATED_ITEM,
        item_id="knowledge-a",
    )
    medium_b = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM,
        item_id="knowledge-b",
    )
    medium_a = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM,
        item_id="knowledge-a",
    )
    high = build_contradiction_gap()

    recommendations = (
        ResearchRecommendationGenerator()
        .generate_all(
            (
                low,
                medium_b,
                high,
                medium_a,
            )
        )
    )

    assert tuple(
        recommendation.priority
        for recommendation
        in recommendations
    ) == (
        ResearchRecommendationPriority.HIGH,
        ResearchRecommendationPriority.MEDIUM,
        ResearchRecommendationPriority.MEDIUM,
        ResearchRecommendationPriority.LOW,
    )
    assert tuple(
        recommendation.gap.items[0].id
        for recommendation
        in recommendations[1:3]
    ) == (
        "knowledge-a",
        "knowledge-b",
    )


def test_generate_all_deduplicates_recommendations(
) -> None:
    first = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM
    )
    second = build_single_item_gap(
        KnowledgeGapType.UNSUPPORTED_ITEM
    )

    recommendations = (
        ResearchRecommendationGenerator()
        .generate_all((first, second))
    )

    assert len(recommendations) == 1


def test_generate_all_accepts_empty_tuple(
) -> None:
    assert (
        ResearchRecommendationGenerator()
        .generate_all(())
        == ()
    )


@pytest.mark.parametrize(
    "gap",
    (
        object(),
        None,
        "gap",
    ),
)
def test_generate_rejects_non_gap(
    gap: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="gap must be a KnowledgeGap",
    ):
        (
            ResearchRecommendationGenerator()
            .generate(
                gap,  # type: ignore[arg-type]
            )
        )


@pytest.mark.parametrize(
    "gaps",
    (
        [],
        set(),
        None,
    ),
)
def test_generate_all_requires_tuple(
    gaps: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="gaps must be a tuple",
    ):
        (
            ResearchRecommendationGenerator()
            .generate_all(
                gaps,  # type: ignore[arg-type]
            )
        )


def test_generate_all_rejects_non_gap_item(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each gap must be a KnowledgeGap"
        ),
    ):
        (
            ResearchRecommendationGenerator()
            .generate_all(
                (
                    object(),  # type: ignore[arg-type]
                )
            )
        )
