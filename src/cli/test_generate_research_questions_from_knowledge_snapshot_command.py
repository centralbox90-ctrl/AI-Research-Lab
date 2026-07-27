from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.application.knowledge_graph_snapshot_loader import (
    KnowledgeGraphSnapshotLoader,
)
from src.cli.generate_research_questions_from_knowledge_snapshot_command import (
    GenerateResearchQuestionsFromKnowledgeSnapshotCommand,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.question import ResearchQuestion


class StubSnapshotLoader(
    KnowledgeGraphSnapshotLoader
):
    def __init__(
        self,
        result: KnowledgeGraphSnapshot,
    ) -> None:
        self.result = result
        self.paths: list[str | Path] = []

    def load(
        self,
        path: str | Path,
    ) -> KnowledgeGraphSnapshot:
        self.paths.append(path)

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


def build_snapshot() -> KnowledgeGraphSnapshot:
    return KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )


def build_question() -> ResearchQuestion:
    return ResearchQuestion(
        id="question-a",
        statement="What evidence is missing?",
        description="Investigate the knowledge gap.",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )


def build_command(
) -> tuple[
    GenerateResearchQuestionsFromKnowledgeSnapshotCommand,
    StubApplication,
    StubSnapshotLoader,
]:
    snapshot = build_snapshot()
    application = StubApplication(
        (build_question(),)
    )
    loader = StubSnapshotLoader(snapshot)

    return (
        GenerateResearchQuestionsFromKnowledgeSnapshotCommand(
            application=application,
            snapshot_loader=loader,
        ),
        application,
        loader,
    )


def test_loads_snapshot_generates_questions_and_renders_artifact(
) -> None:
    command, application, loader = build_command()
    snapshot_path = Path(
        "knowledge-snapshot.json"
    )

    rendered = command.execute(
        snapshot_path
    )
    payload = json.loads(rendered)

    assert loader.paths == [
        snapshot_path,
    ]
    assert application.snapshots == [
        loader.result,
    ]
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["artifact_version"] == 1
    assert payload["snapshot_fingerprint"] == (
        loader.result.fingerprint
    )
    assert payload["question_count"] == 1
    assert payload["questions"][0]["id"] == (
        "question-a"
    )


def test_supports_compact_json() -> None:
    command, _, _ = build_command()

    rendered = command.execute(
        "knowledge-snapshot.json",
        indent=None,
    )

    assert "\n" not in rendered
    assert json.loads(rendered)[
        "question_count"
    ] == 1


def test_rejects_invalid_application() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "application must be a "
            "GenerateResearchQuestionsFromKnowledgeSnapshot"
        ),
    ):
        GenerateResearchQuestionsFromKnowledgeSnapshotCommand(
            application=object(),
        )


def test_rejects_invalid_snapshot_loader() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot_loader must be a "
            "KnowledgeGraphSnapshotLoader or None"
        ),
    ):
        GenerateResearchQuestionsFromKnowledgeSnapshotCommand(
            application=StubApplication(
                ()
            ),
            snapshot_loader=object(),
        )
