from datetime import UTC, datetime

import pytest

from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
from src.application.hypothesis_evaluation_artifact_loader import (
    HypothesisEvaluationArtifactLoader,
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
        return "artifact-loader-test"


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:loader-example"
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
        limitations=("generated data",),
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
            provenance=(("producer", "test"),),
        ),
        valid_from=CREATED_AT,
        change_reason=(
            "Promoted from hypothesis evaluation."
        ),
        supersedes_version=None,
    )


def present_evaluation(
    evaluation: HypothesisEvaluation,
) -> dict[str, object]:
    return {
        **evaluation.to_dict(),
        "fingerprint": evaluation.fingerprint,
    }


def present_revision(
    revision: KnowledgeRevision,
) -> dict[str, object]:
    return {
        **revision.to_dict(),
        "fingerprint": revision.fingerprint,
    }


def build_envelope_factory(
) -> HypothesisEvaluationArtifactEnvelopeFactory:
    return HypothesisEvaluationArtifactEnvelopeFactory(
        envelope_factory=(
            ResearchArtifactEnvelopeFactory(
                producer="loader-test",
                producer_version="git:test",
                clock=FixedClock(),
                id_generator=FixedIdGenerator(),
            )
        )
    )


def test_loads_legacy_version_one(
) -> None:
    evaluation = build_evaluation()
    serialized = {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 1,
        "evaluation": present_evaluation(
            evaluation
        ),
    }

    loaded = (
        HypothesisEvaluationArtifactLoader()
        .load(serialized)
    )

    assert loaded.evaluation == evaluation
    assert loaded.knowledge_revision is None
    assert loaded.envelope is None


def test_loads_legacy_version_two(
) -> None:
    evaluation = build_evaluation()
    revision = build_revision()
    serialized = {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 2,
        "evaluation": present_evaluation(
            evaluation
        ),
        "knowledge_revision": present_revision(
            revision
        ),
    }

    loaded = (
        HypothesisEvaluationArtifactLoader()
        .load(serialized)
    )

    assert loaded.evaluation == evaluation
    assert loaded.knowledge_revision == revision
    assert loaded.envelope is None


def test_loads_envelope_payload_version_one(
) -> None:
    evaluation = build_evaluation()
    serialized = (
        build_envelope_factory()
        .create(
            evaluation=evaluation,
            correlation_id="research-rsi",
        )
        .to_dict()
    )

    loaded = (
        HypothesisEvaluationArtifactLoader()
        .load(serialized)
    )

    assert loaded.evaluation == evaluation
    assert loaded.knowledge_revision is None
    assert loaded.envelope is not None
    assert loaded.envelope.artifact_id == (
        "artifact-loader-test"
    )
    assert loaded.envelope.correlation_id == (
        "research-rsi"
    )


def test_loads_envelope_payload_version_two(
) -> None:
    evaluation = build_evaluation()
    revision = build_revision()
    serialized = (
        build_envelope_factory()
        .create(
            evaluation=evaluation,
            knowledge_revision=revision,
        )
        .to_dict()
    )

    loaded = (
        HypothesisEvaluationArtifactLoader()
        .load(serialized)
    )

    assert loaded.evaluation == evaluation
    assert loaded.knowledge_revision == revision
    assert loaded.envelope is not None
    assert (
        loaded.envelope.payload_schema_version
        == 2
    )


def test_rejects_changed_evaluation_fingerprint(
) -> None:
    evaluation = build_evaluation()
    serialized = {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 1,
        "evaluation": present_evaluation(
            evaluation
        ),
    }
    serialized["evaluation"]["fingerprint"] = (
        "0" * 64
    )

    with pytest.raises(
        ValueError,
        match=(
            "evaluation fingerprint "
            "does not match"
        ),
    ):
        HypothesisEvaluationArtifactLoader().load(
            serialized
        )


def test_rejects_changed_envelope_payload(
) -> None:
    serialized = (
        build_envelope_factory()
        .create(
            evaluation=build_evaluation(),
        )
        .to_dict()
    )
    serialized["payload"]["evaluation"][
        "confidence"
    ] = 0.5

    with pytest.raises(
        ValueError,
        match=(
            "payload_fingerprint does not "
            "match payload"
        ),
    ):
        HypothesisEvaluationArtifactLoader().load(
            serialized
        )


def test_rejects_wrong_artifact_type(
) -> None:
    serialized = {
        "artifact_type": "finding",
        "artifact_version": 1,
        "evaluation": present_evaluation(
            build_evaluation()
        ),
    }

    with pytest.raises(
        ValueError,
        match=(
            "artifact_type must be "
            "hypothesis_evaluation"
        ),
    ):
        HypothesisEvaluationArtifactLoader().load(
            serialized
        )


def test_rejects_unsupported_legacy_version(
) -> None:
    serialized = {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 3,
        "evaluation": present_evaluation(
            build_evaluation()
        ),
    }

    with pytest.raises(
        ValueError,
        match="artifact_version must be 1 or 2",
    ):
        HypothesisEvaluationArtifactLoader().load(
            serialized
        )


def test_rejects_unknown_payload_field(
) -> None:
    evaluation = build_evaluation()
    serialized = {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 1,
        "evaluation": {
            **present_evaluation(evaluation),
            "runtime_callback": "unsafe",
        },
    }

    with pytest.raises(
        ValueError,
        match=(
            "evaluation unknown fields: "
            "runtime_callback"
        ),
    ):
        HypothesisEvaluationArtifactLoader().load(
            serialized
        )
