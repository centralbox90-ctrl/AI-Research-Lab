from datetime import datetime, timezone

import pytest

from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.application.research_recommendation_question_adapter import (
    ResearchRecommendationQuestionAdapter,
)
from src.research.knowledge_gap_detector import (
    KnowledgeGapDetector,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.research_recommendation import (
    ResearchRecommendation,
    ResearchRecommendationPriority,
)
from src.research.research_recommendation_generator import (
    ResearchRecommendationGenerator,
)
from src.research.research_types import ResearchStatus


CREATED_AT = datetime(
    2026,
    7,
    27,
    12,
    30,
    tzinfo=timezone.utc,
)


def build_item(
    item_id: str,
    *,
    statement: str | None = None,
    applicability: tuple[str, ...] = (
        "liquid markets",
    ),
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=(
            statement
            or f"Statement {item_id}."
        ),
        confidence=0.85,
        applicability=applicability,
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


def build_relation(
    source: KnowledgeItem,
    target: KnowledgeItem,
    relation_type: KnowledgeRelationType,
) -> KnowledgeRelation:
    return KnowledgeRelation(
        source=source,
        target=target,
        relation_type=relation_type,
        reason="Explicit graph relation.",
    )


def build_service(
    *,
    clock=lambda: CREATED_AT,
    id_factory=lambda recommendation: (
        "question-"
        + recommendation.fingerprint[:16]
    ),
) -> GenerateResearchQuestionsFromKnowledgeSnapshot:
    return GenerateResearchQuestionsFromKnowledgeSnapshot(
        gap_detector=KnowledgeGapDetector(),
        recommendation_generator=(
            ResearchRecommendationGenerator()
        ),
        question_adapter=(
            ResearchRecommendationQuestionAdapter(
                clock=clock,
                id_factory=id_factory,
            )
        ),
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "gap_detector",
        "recommendation_generator",
        "question_adapter",
    ),
    (
        (
            "gap_detector",
            object(),
            ResearchRecommendationGenerator(),
            ResearchRecommendationQuestionAdapter(
                clock=lambda: CREATED_AT,
                id_factory=lambda _: "question-a",
            ),
        ),
        (
            "recommendation_generator",
            KnowledgeGapDetector(),
            object(),
            ResearchRecommendationQuestionAdapter(
                clock=lambda: CREATED_AT,
                id_factory=lambda _: "question-a",
            ),
        ),
        (
            "question_adapter",
            KnowledgeGapDetector(),
            ResearchRecommendationGenerator(),
            object(),
        ),
    ),
)
def test_requires_typed_dependencies(
    field_name: str,
    gap_detector: object,
    recommendation_generator: object,
    question_adapter: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be a "
        ),
    ):
        GenerateResearchQuestionsFromKnowledgeSnapshot(
            gap_detector=gap_detector,  # type: ignore[arg-type]
            recommendation_generator=(  # type: ignore[arg-type]
                recommendation_generator
            ),
            question_adapter=question_adapter,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "snapshot",
    (
        object(),
        None,
        (),
    ),
)
def test_requires_graph_snapshot(
    snapshot: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot must be a "
            "KnowledgeGraphSnapshot"
        ),
    ):
        build_service().execute(
            snapshot,  # type: ignore[arg-type]
        )


def test_empty_snapshot_returns_empty_tuple(
) -> None:
    snapshot = KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )

    assert build_service().execute(snapshot) == ()


def test_empty_snapshot_does_not_call_policies(
) -> None:
    def fail_clock() -> datetime:
        raise AssertionError(
            "clock must not be called"
        )

    def fail_id_factory(
        _: ResearchRecommendation,
    ) -> str:
        raise AssertionError(
            "id_factory must not be called"
        )

    snapshot = KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )

    assert (
        build_service(
            clock=fail_clock,
            id_factory=fail_id_factory,
        ).execute(snapshot)
        == ()
    )


def test_generates_question_for_isolated_item(
) -> None:
    item = build_item(
        "knowledge-a",
        statement="Momentum persists.",
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )

    questions = build_service().execute(
        snapshot
    )

    assert len(questions) == 1
    question = questions[0]
    assert question.id.startswith("question-")
    assert question.statement == (
        'How can "Momentum persists." '
        "be connected to existing knowledge?"
    )
    assert question.created_at == CREATED_AT
    assert question.status is ResearchStatus.NEW
    assert "Priority: low" in (
        question.description
    )
    assert "Applicability: liquid markets" in (
        question.description
    )


def test_orders_questions_by_recommendation_priority(
) -> None:
    isolated = build_item("knowledge-c")
    left = build_item(
        "knowledge-a",
        statement="Momentum persists.",
    )
    right = build_item(
        "knowledge-b",
        statement="Momentum reverses.",
    )
    contradiction = build_relation(
        left,
        right,
        KnowledgeRelationType.CONTRADICTS,
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(isolated, right, left),
        relations=(contradiction,),
    )

    questions = build_service().execute(
        snapshot
    )

    assert len(questions) == 4
    assert tuple(
        question.description.splitlines()[1]
        for question in questions
    ) == (
        "Priority: high",
        "Priority: medium",
        "Priority: medium",
        "Priority: low",
    )


def test_passes_ordered_recommendations_to_id_policy(
) -> None:
    isolated = build_item("knowledge-c")
    left = build_item("knowledge-a")
    right = build_item("knowledge-b")
    contradiction = build_relation(
        left,
        right,
        KnowledgeRelationType.CONTRADICTS,
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(isolated, left, right),
        relations=(contradiction,),
    )
    received: list[
        ResearchRecommendation
    ] = []

    def id_factory(
        recommendation: ResearchRecommendation,
    ) -> str:
        received.append(recommendation)
        return f"question-{len(received)}"

    questions = build_service(
        id_factory=id_factory,
    ).execute(snapshot)

    assert tuple(
        recommendation.priority
        for recommendation in received
    ) == (
        ResearchRecommendationPriority.HIGH,
        ResearchRecommendationPriority.MEDIUM,
        ResearchRecommendationPriority.MEDIUM,
        ResearchRecommendationPriority.LOW,
    )
    assert tuple(
        question.id
        for question in questions
    ) == (
        "question-1",
        "question-2",
        "question-3",
        "question-4",
    )


def test_preserves_gap_and_recommendation_provenance(
) -> None:
    item = build_item("knowledge-a")
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )
    received: list[
        ResearchRecommendation
    ] = []

    def id_factory(
        recommendation: ResearchRecommendation,
    ) -> str:
        received.append(recommendation)
        return "question-a"

    question = build_service(
        id_factory=id_factory,
    ).execute(snapshot)[0]
    recommendation = received[0]

    assert recommendation.gap.snapshot_fingerprint == (
        snapshot.fingerprint
    )
    assert (
        recommendation.gap.fingerprint
        in question.description
    )
    assert (
        recommendation.fingerprint
        in question.description
    )


def test_calls_clock_once_per_question(
) -> None:
    left = build_item("knowledge-a")
    right = build_item("knowledge-b")
    relation = build_relation(
        left,
        right,
        KnowledgeRelationType.EXTENDS,
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(left, right),
        relations=(relation,),
    )
    clock_calls = 0

    def clock() -> datetime:
        nonlocal clock_calls
        clock_calls += 1
        return CREATED_AT

    questions = build_service(
        clock=clock,
    ).execute(snapshot)

    assert len(questions) == 2
    assert clock_calls == 2


def test_rejects_duplicate_generated_ids(
) -> None:
    left = build_item("knowledge-a")
    right = build_item("knowledge-b")
    relation = build_relation(
        left,
        right,
        KnowledgeRelationType.EXTENDS,
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(left, right),
        relations=(relation,),
    )

    with pytest.raises(
        ValueError,
        match=(
            "generated question IDs "
            "must be unique"
        ),
    ):
        build_service(
            id_factory=lambda _: "duplicate-id",
        ).execute(snapshot)


def test_is_deterministic_for_fixed_policies(
) -> None:
    item = build_item("knowledge-a")
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )
    service = build_service(
        id_factory=lambda _: "question-a",
    )

    first = service.execute(snapshot)
    second = service.execute(snapshot)

    assert first == second
    assert tuple(
        question.to_dict()
        for question in first
    ) == tuple(
        question.to_dict()
        for question in second
    )
