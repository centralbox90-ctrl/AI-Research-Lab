from datetime import UTC, datetime

import pytest

from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    12,
    0,
    tzinfo=UTC,
)


class FixedClock:
    def now(self) -> datetime:
        return CREATED_AT


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-hypothesis-001"


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:envelope-example"
        ),
        hypothesis_id="hypothesis-rsi",
        state=HypothesisEvaluationState.SUPPORTED,
        confidence=0.82,
        finding_refs=(
            "finding-a",
            "finding-b",
        ),
        rationale=(
            "Replicated findings support the hypothesis.",
        ),
        limitations=(),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )


def build_revision() -> KnowledgeRevision:
    return KnowledgeRevision(
        item=KnowledgeItem(
            id="knowledge-rsi",
            statement=(
                "RSI effect persists across markets."
            ),
            confidence=0.82,
            applicability=("liquid FX",),
            limitations=("generated data",),
            supporting_findings=(
                "finding-a",
                "finding-b",
            ),
            version=1,
            provenance=(
                ("producer", "test"),
            ),
        ),
        valid_from=CREATED_AT,
        change_reason=(
            "Promoted from hypothesis evaluation."
        ),
        supersedes_version=None,
    )


def build_factory(
) -> HypothesisEvaluationArtifactEnvelopeFactory:
    return HypothesisEvaluationArtifactEnvelopeFactory(
        envelope_factory=(
            ResearchArtifactEnvelopeFactory(
                producer=(
                    "comparative-hypothesis-evaluation"
                ),
                producer_version="git:abc123",
                clock=FixedClock(),
                id_generator=FixedIdGenerator(),
            )
        )
    )


def test_creates_evaluation_envelope(
) -> None:
    evaluation = build_evaluation()

    envelope = build_factory().create(
        evaluation=evaluation,
        correlation_id="research-rsi",
    )
    serialized = envelope.to_dict()

    assert envelope.artifact_type == (
        "hypothesis_evaluation"
    )
    assert envelope.payload_schema_version == 1
    assert envelope.artifact_id == (
        "artifact-hypothesis-001"
    )
    assert envelope.created_at == CREATED_AT
    assert envelope.correlation_id == (
        "research-rsi"
    )
    assert serialized["payload"]["evaluation"][
        "id"
    ] == evaluation.id
    assert serialized["payload"]["evaluation"][
        "fingerprint"
    ] == evaluation.fingerprint
    assert "knowledge_revision" not in (
        serialized["payload"]
    )
    assert envelope.provenance[
        "evaluation_plan_version"
    ] == "hypothesis-evaluation-v1"
    assert envelope.provenance[
        "hypothesis_id"
    ] == "hypothesis-rsi"
    assert len(envelope.source_references) == 1

    evaluation_reference = (
        envelope.source_references[0]
    )

    assert evaluation_reference.reference_type == (
        "hypothesis_evaluation"
    )
    assert evaluation_reference.reference_id == (
        evaluation.id
    )
    assert (
        evaluation_reference.reference_fingerprint
        == evaluation.fingerprint
    )


def test_creates_promoted_evaluation_envelope(
) -> None:
    evaluation = build_evaluation()
    revision = build_revision()

    envelope = build_factory().create(
        evaluation=evaluation,
        knowledge_revision=revision,
    )
    serialized = envelope.to_dict()

    assert envelope.payload_schema_version == 2
    assert serialized["payload"][
        "knowledge_revision"
    ]["item"]["id"] == "knowledge-rsi"
    assert serialized["payload"][
        "knowledge_revision"
    ]["fingerprint"] == revision.fingerprint
    assert len(envelope.source_references) == 2

    revision_reference = (
        envelope.source_references[1]
    )

    assert revision_reference.reference_type == (
        "knowledge_revision"
    )
    assert revision_reference.reference_id == (
        "knowledge-rsi"
    )
    assert revision_reference.reference_version == 1
    assert (
        revision_reference.reference_fingerprint
        == revision.fingerprint
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
        HypothesisEvaluationArtifactEnvelopeFactory(
            envelope_factory=object(),
        )


def test_rejects_invalid_evaluation(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "evaluation must be a "
            "HypothesisEvaluation"
        ),
    ):
        build_factory().create(
            evaluation=object(),
        )


def test_rejects_invalid_knowledge_revision(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "knowledge_revision must be a "
            "KnowledgeRevision or None"
        ),
    ):
        build_factory().create(
            evaluation=build_evaluation(),
            knowledge_revision=object(),
        )
