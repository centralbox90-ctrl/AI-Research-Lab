from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.cli.generate_research_questions_from_knowledge_repositories_command import (
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import (
    KnowledgeItem,
)
from src.research.question import (
    ResearchQuestion,
)


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


class StubApplication(
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


def _snapshot() -> KnowledgeGraphSnapshot:
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


def _question() -> ResearchQuestion:
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


def _command(
) -> tuple[
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
    StubSnapshotBuilder,
    StubApplication,
]:
    builder = StubSnapshotBuilder(
        _snapshot()
    )
    application = StubApplication(
        (_question(),)
    )

    return (
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand(
            snapshot_builder=builder,
            application=application,
        ),
        builder,
        application,
    )


def test_builds_snapshot_generates_and_renders():
    command, builder, application = (
        _command()
    )

    rendered = command.execute()
    payload = json.loads(rendered)

    assert builder.call_count == 1
    assert application.snapshots == [
        builder.result
    ]
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["artifact_version"] == 1
    assert payload["snapshot_fingerprint"] == (
        builder.result.fingerprint
    )
    assert payload["question_count"] == 1
    assert payload["questions"][0]["id"] == (
        "question-1"
    )


def test_supports_compact_json():
    command, _, _ = _command()

    rendered = command.execute(
        indent=None
    )

    assert "\n" not in rendered
    assert json.loads(rendered)[
        "question_count"
    ] == 1


@pytest.mark.parametrize(
    "dependency",
    (
        "snapshot_builder",
        "application",
    ),
)
def test_requires_application_dependencies(
    dependency: str,
):
    builder = StubSnapshotBuilder(
        _snapshot()
    )
    application = StubApplication(())
    arguments = {
        "snapshot_builder": builder,
        "application": application,
    }
    arguments[dependency] = object()

    with pytest.raises(TypeError):
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand(
            **arguments
        )
