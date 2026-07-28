from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.generate_research_questions_from_knowledge_repositories import (
    KnowledgeResearchQuestionsResult,
)
from src.application.knowledge_research_questions_artifact_envelope_factory import (
    KnowledgeResearchQuestionsArtifactEnvelopeFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.question import ResearchQuestion


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            28,
            12,
            0,
            tzinfo=UTC,
        )


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-knowledge-questions"


def build_result(
) -> KnowledgeResearchQuestionsResult:
    snapshot = KnowledgeGraphSnapshot(
        items=(
            KnowledgeItem(
                id="knowledge-1",
                statement="Momentum persists.",
                confidence=0.85,
                applicability=(
                    "liquid markets",
                ),
                limitations=(
                    "limited history",
                ),
                supporting_findings=(
                    "finding-1",
                    "finding-2",
                ),
                version=1,
                provenance=(
                    ("producer", "test"),
                ),
            ),
        ),
        relations=(),
    )
    question = ResearchQuestion(
        id="question-1",
        statement=(
            "Does momentum persist "
            "outside liquid markets?"
        ),
        description=(
            "Test the current applicability boundary."
        ),
        created_at=datetime(
            2026,
            7,
            28,
            13,
            0,
            tzinfo=UTC,
        ),
    )

    return KnowledgeResearchQuestionsResult(
        snapshot=snapshot,
        questions=(question,),
    )


def build_factory(
) -> KnowledgeResearchQuestionsArtifactEnvelopeFactory:
    return (
        KnowledgeResearchQuestionsArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer=(
                        "knowledge-question-generator"
                    ),
                    producer_version="git:test",
                    clock=FixedClock(),
                    id_generator=FixedIdGenerator(),
                )
            )
        )
    )


def test_creates_reproducible_question_envelope(
) -> None:
    result = build_result()

    envelope = build_factory().create(
        result=result,
        correlation_id=" lifecycle-42 ",
    )
    serialized = envelope.to_dict()

    assert serialized["schema_version"] == 1
    assert serialized["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert serialized[
        "payload_schema_version"
    ] == 1
    assert serialized["artifact_id"] == (
        "artifact-knowledge-questions"
    )
    assert serialized["producer"] == (
        "knowledge-question-generator"
    )
    assert serialized["producer_version"] == (
        "git:test"
    )
    assert serialized["correlation_id"] == (
        "lifecycle-42"
    )
    assert len(
        serialized["payload_fingerprint"]
    ) == 64

    payload = serialized["payload"]

    assert payload["snapshot"] == (
        result.snapshot.to_dict()
    )
    assert payload["snapshot_fingerprint"] == (
        result.snapshot.fingerprint
    )
    assert payload["question_count"] == 1
    assert payload["questions"][0]["id"] == (
        "question-1"
    )

    assert serialized["provenance"] == {
        "knowledge_item_count": 1,
        "knowledge_relation_count": 0,
        "knowledge_snapshot_fingerprint": (
            result.snapshot.fingerprint
        ),
    }
    assert serialized["source_references"] == [
        {
            "reference_type": (
                "knowledge_graph_snapshot"
            ),
            "reference_id": (
                result.snapshot.fingerprint
            ),
            "reference_version": None,
            "reference_fingerprint": (
                result.snapshot.fingerprint
            ),
        },
    ]


def test_supports_empty_question_result(
) -> None:
    result = KnowledgeResearchQuestionsResult(
        snapshot=KnowledgeGraphSnapshot(
            items=(),
            relations=(),
        ),
        questions=(),
    )

    envelope = build_factory().create(
        result=result
    )

    assert envelope.to_dict()["payload"][
        "question_count"
    ] == 0
    assert envelope.to_dict()["payload"][
        "questions"
    ] == []


def test_rejects_invalid_result() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "result must be a "
            "KnowledgeResearchQuestionsResult"
        ),
    ):
        build_factory().create(
            result=object(),
        )


def test_rejects_invalid_envelope_factory(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "envelope_factory must be a "
            "ResearchArtifactEnvelopeFactory"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactEnvelopeFactory(
                envelope_factory=object(),
            )
        )
