from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.generate_research_questions_from_knowledge_repositories import (
    GenerateResearchQuestionsFromKnowledgeRepositories,
    KnowledgeResearchQuestionsResult,
)
from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.question import ResearchQuestion


class StubSnapshotBuilder(
    BuildKnowledgeGraphSnapshot
):
    def __init__(
        self,
        result: KnowledgeGraphSnapshot,
    ) -> None:
        self.result = result
        self.call_count = 0

    def execute(
        self,
    ) -> KnowledgeGraphSnapshot:
        self.call_count += 1
        return self.result


class StubQuestionGenerator(
    GenerateResearchQuestionsFromKnowledgeSnapshot
):
    def __init__(
        self,
        result: tuple[ResearchQuestion, ...],
    ) -> None:
        self.result = result
        self.snapshots: list[
            KnowledgeGraphSnapshot
        ] = []

    def execute(
        self,
        snapshot: KnowledgeGraphSnapshot,
    ) -> tuple[ResearchQuestion, ...]:
        self.snapshots.append(snapshot)
        return self.result


def build_snapshot() -> KnowledgeGraphSnapshot:
    item = KnowledgeItem(
        id="knowledge-1",
        statement="Momentum persists.",
        confidence=0.85,
        applicability=("liquid markets",),
        limitations=("limited history",),
        supporting_findings=(
            "finding-1",
            "finding-2",
        ),
        version=1,
        provenance=(("producer", "test"),),
    )

    return KnowledgeGraphSnapshot(
        items=(item,),
        relations=(),
    )


def build_question(
    question_id: str = "question-1",
) -> ResearchQuestion:
    return ResearchQuestion(
        id=question_id,
        statement="What evidence is missing?",
        description=(
            "Investigate the isolated knowledge item."
        ),
        created_at=datetime(
            2026,
            7,
            28,
            12,
            0,
            tzinfo=UTC,
        ),
    )


def test_builds_snapshot_and_generates_questions(
) -> None:
    snapshot = build_snapshot()
    questions = (build_question(),)
    snapshot_builder = StubSnapshotBuilder(
        snapshot
    )
    question_generator = StubQuestionGenerator(
        questions
    )
    application = (
        GenerateResearchQuestionsFromKnowledgeRepositories(
            snapshot_builder=snapshot_builder,
            question_generator=question_generator,
        )
    )

    result = application.execute()

    assert isinstance(
        result,
        KnowledgeResearchQuestionsResult,
    )
    assert result.snapshot is snapshot
    assert result.questions is questions
    assert snapshot_builder.call_count == 1
    assert question_generator.snapshots == [
        snapshot
    ]


@pytest.mark.parametrize(
    "dependency",
    (
        "snapshot_builder",
        "question_generator",
    ),
)
def test_requires_declared_dependencies(
    dependency: str,
) -> None:
    arguments = {
        "snapshot_builder": StubSnapshotBuilder(
            build_snapshot()
        ),
        "question_generator": StubQuestionGenerator(
            ()
        ),
    }
    arguments[dependency] = object()

    with pytest.raises(TypeError):
        GenerateResearchQuestionsFromKnowledgeRepositories(
            **arguments
        )


def test_result_rejects_invalid_snapshot(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot must be a "
            "KnowledgeGraphSnapshot"
        ),
    ):
        KnowledgeResearchQuestionsResult(
            snapshot=object(),
            questions=(),
        )


def test_result_rejects_non_tuple_questions(
) -> None:
    with pytest.raises(
        TypeError,
        match="questions must be a tuple",
    ):
        KnowledgeResearchQuestionsResult(
            snapshot=build_snapshot(),
            questions=[],
        )


def test_result_rejects_invalid_question(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "questions must contain only "
            "ResearchQuestion values"
        ),
    ):
        KnowledgeResearchQuestionsResult(
            snapshot=build_snapshot(),
            questions=(object(),),
        )


def test_result_rejects_duplicate_question_ids(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "questions must have unique IDs"
        ),
    ):
        KnowledgeResearchQuestionsResult(
            snapshot=build_snapshot(),
            questions=(
                build_question(),
                build_question(),
            ),
        )
