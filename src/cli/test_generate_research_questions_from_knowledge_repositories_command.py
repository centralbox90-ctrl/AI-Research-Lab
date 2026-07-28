from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from src.application.generate_research_questions_from_knowledge_repositories import (
    GenerateResearchQuestionsFromKnowledgeRepositories,
    KnowledgeResearchQuestionsResult,
)
from src.cli.generate_research_questions_from_knowledge_repositories_command import (
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.question import ResearchQuestion


class StubApplication(
    GenerateResearchQuestionsFromKnowledgeRepositories
):
    def __init__(
        self,
        result: KnowledgeResearchQuestionsResult,
    ) -> None:
        self.result = result
        self.call_count = 0

    def execute(
        self,
    ) -> KnowledgeResearchQuestionsResult:
        self.call_count += 1
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


def build_question() -> ResearchQuestion:
    return ResearchQuestion(
        id="question-1",
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


def build_result(
) -> KnowledgeResearchQuestionsResult:
    return KnowledgeResearchQuestionsResult(
        snapshot=build_snapshot(),
        questions=(build_question(),),
    )


def build_command(
) -> tuple[
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
    StubApplication,
]:
    application = StubApplication(
        build_result()
    )

    return (
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand(
            application=application,
        ),
        application,
    )


def test_renders_application_result() -> None:
    command, application = build_command()

    rendered = command.execute()
    payload = json.loads(rendered)

    assert application.call_count == 1
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["artifact_version"] == 1
    assert payload["snapshot_fingerprint"] == (
        application.result.snapshot.fingerprint
    )
    assert payload["question_count"] == 1
    assert payload["questions"][0]["id"] == (
        "question-1"
    )


def test_supports_compact_json() -> None:
    command, application = build_command()

    rendered = command.execute(
        indent=None
    )

    assert application.call_count == 1
    assert "\n" not in rendered
    assert json.loads(rendered)[
        "question_count"
    ] == 1


def test_requires_application_dependency(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "application must be a "
            "GenerateResearchQuestionsFromKnowledgeRepositories"
        ),
    ):
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand(
            application=object(),
        )
