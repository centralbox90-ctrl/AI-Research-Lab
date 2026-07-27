from datetime import datetime, timezone

import pytest

from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.application.knowledge_research_question_application import (
    build_knowledge_research_question_application,
    fingerprint_research_question_id,
    system_utc_clock,
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
)
from src.research.research_recommendation_generator import (
    ResearchRecommendationGenerator,
)


CREATED_AT = datetime(
    2026,
    7,
    27,
    18,
    0,
    tzinfo=timezone.utc,
)


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


def build_recommendation(
) -> ResearchRecommendation:
    item = build_item("knowledge-a")
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )
    gap = KnowledgeGapDetector().detect(
        snapshot
    )[0]

    return (
        ResearchRecommendationGenerator()
        .generate(gap)
    )


def test_system_clock_returns_aware_utc(
) -> None:
    before = datetime.now(timezone.utc)
    result = system_utc_clock()
    after = datetime.now(timezone.utc)

    assert result.tzinfo is timezone.utc
    assert before <= result <= after


def test_fingerprint_policy_is_stable(
) -> None:
    recommendation = build_recommendation()

    first = fingerprint_research_question_id(
        recommendation
    )
    second = fingerprint_research_question_id(
        recommendation
    )

    assert first == second
    assert first == (
        "knowledge-question-"
        + recommendation.fingerprint
    )


def test_fingerprint_policy_rejects_invalid_value(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "recommendation must be a "
            "ResearchRecommendation"
        ),
    ):
        fingerprint_research_question_id(
            object(),  # type: ignore[arg-type]
        )


def test_builds_ready_application_service(
) -> None:
    application = (
        build_knowledge_research_question_application()
    )

    assert isinstance(
        application,
        GenerateResearchQuestionsFromKnowledgeSnapshot,
    )


def test_built_application_handles_empty_snapshot(
) -> None:
    application = (
        build_knowledge_research_question_application()
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )

    assert application.execute(snapshot) == ()


def test_default_id_references_recommendation(
) -> None:
    item = build_item(
        "knowledge-a",
        statement="Momentum persists.",
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )
    recommendation = (
        ResearchRecommendationGenerator()
        .generate_all(
            KnowledgeGapDetector().detect(
                snapshot
            )
        )[0]
    )

    question = (
        build_knowledge_research_question_application()
        .execute(snapshot)[0]
    )

    assert question.id == (
        "knowledge-question-"
        + recommendation.fingerprint
    )
    assert question.created_at.tzinfo is (
        timezone.utc
    )


def test_custom_policies_are_used(
) -> None:
    received: list[
        ResearchRecommendation
    ] = []

    def id_factory(
        recommendation: ResearchRecommendation,
    ) -> str:
        received.append(recommendation)
        return "custom-question-id"

    item = build_item("knowledge-a")
    snapshot = KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )
    application = (
        build_knowledge_research_question_application(
            clock=lambda: CREATED_AT,
            id_factory=id_factory,
        )
    )

    question = application.execute(snapshot)[0]

    assert question.id == "custom-question-id"
    assert question.created_at == CREATED_AT
    assert len(received) == 1
    assert received[0].question == (
        question.statement
    )


def test_default_ids_are_unique_for_batch(
) -> None:
    left = build_item("knowledge-a")
    right = build_item("knowledge-b")
    relation = KnowledgeRelation(
        source=left,
        target=right,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Explicit graph relation.",
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(left, right),
        relations=(relation,),
    )

    questions = (
        build_knowledge_research_question_application()
        .execute(snapshot)
    )

    assert len(questions) == 2
    assert len(
        {
            question.id
            for question in questions
        }
    ) == 2


@pytest.mark.parametrize(
    ("field_name", "clock", "id_factory"),
    (
        (
            "clock",
            None,
            fingerprint_research_question_id,
        ),
        (
            "id_factory",
            system_utc_clock,
            None,
        ),
    ),
)
def test_rejects_invalid_custom_policies(
    field_name: str,
    clock: object,
    id_factory: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be callable",
    ):
        build_knowledge_research_question_application(
            clock=clock,  # type: ignore[arg-type]
            id_factory=id_factory,  # type: ignore[arg-type]
        )
