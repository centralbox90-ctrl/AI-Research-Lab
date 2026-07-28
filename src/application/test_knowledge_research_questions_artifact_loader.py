from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.generate_research_questions_from_knowledge_repositories import (
    KnowledgeResearchQuestionsResult,
)
from src.application.knowledge_research_questions_artifact_envelope_factory import (
    KnowledgeResearchQuestionsArtifactEnvelopeFactory,
)
from src.application.knowledge_research_questions_artifact_loader import (
    KnowledgeResearchQuestionsArtifactLoader,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
    fingerprint_research_artifact_payload,
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
            15,
            0,
            tzinfo=UTC,
        )


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-question-loader"


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
            16,
            0,
            tzinfo=UTC,
        ),
    )

    return KnowledgeResearchQuestionsResult(
        snapshot=snapshot,
        questions=(question,),
    )


def build_serialized(
) -> dict[str, object]:
    factory = (
        KnowledgeResearchQuestionsArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer="question-loader-test",
                    producer_version="git:test",
                    clock=FixedClock(),
                    id_generator=FixedIdGenerator(),
                )
            )
        )
    )

    return factory.create(
        result=build_result(),
        correlation_id="research-lifecycle-42",
    ).to_dict()


def refresh_payload_fingerprint(
    serialized: dict[str, object],
) -> None:
    serialized["payload_fingerprint"] = (
        fingerprint_research_artifact_payload(
            serialized["payload"]
        )
    )


def test_loads_typed_question_envelope(
) -> None:
    expected = build_result()

    loaded = (
        KnowledgeResearchQuestionsArtifactLoader()
        .load(build_serialized())
    )

    assert loaded.result == expected
    assert loaded.envelope.artifact_id == (
        "artifact-question-loader"
    )
    assert loaded.envelope.correlation_id == (
        "research-lifecycle-42"
    )
    assert loaded.envelope.source_references[
        0
    ].reference_fingerprint == (
        expected.snapshot.fingerprint
    )


def test_rejects_changed_envelope_payload(
) -> None:
    serialized = build_serialized()
    serialized["payload"]["questions"][0][
        "statement"
    ] = "Changed question."

    with pytest.raises(
        ValueError,
        match=(
            "payload_fingerprint does not "
            "match payload"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_snapshot_fingerprint_mismatch(
) -> None:
    serialized = build_serialized()
    serialized["payload"][
        "snapshot_fingerprint"
    ] = "0" * 64
    refresh_payload_fingerprint(serialized)

    with pytest.raises(
        ValueError,
        match=(
            "snapshot_fingerprint does not "
            "match snapshot"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_question_count_mismatch(
) -> None:
    serialized = build_serialized()
    serialized["payload"]["question_count"] = 2
    refresh_payload_fingerprint(serialized)

    with pytest.raises(
        ValueError,
        match=(
            "question_count does not match "
            "questions"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_wrong_artifact_type(
) -> None:
    serialized = build_serialized()
    serialized["artifact_type"] = (
        "hypothesis_evaluation"
    )

    with pytest.raises(
        ValueError,
        match=(
            "artifact_type must be "
            "knowledge_research_questions"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_unsupported_payload_version(
) -> None:
    serialized = build_serialized()
    serialized["payload_schema_version"] = 2

    with pytest.raises(
        ValueError,
        match="payload_schema_version must be 1",
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_source_reference_mismatch(
) -> None:
    serialized = build_serialized()
    serialized["source_references"][0][
        "reference_id"
    ] = "0" * 64

    with pytest.raises(
        ValueError,
        match=(
            "source_references must identify "
            "the exact Knowledge snapshot"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_unknown_payload_field(
) -> None:
    serialized = build_serialized()
    serialized["payload"]["runtime_callback"] = (
        "unsafe"
    )
    refresh_payload_fingerprint(serialized)

    with pytest.raises(
        ValueError,
        match=(
            "payload unknown fields: "
            "runtime_callback"
        ),
    ):
        (
            KnowledgeResearchQuestionsArtifactLoader()
            .load(serialized)
        )


def test_rejects_invalid_snapshot_loader(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot_loader must be a "
            "KnowledgeGraphSnapshotLoader or None"
        ),
    ):
        KnowledgeResearchQuestionsArtifactLoader(
            snapshot_loader=object(),
        )
