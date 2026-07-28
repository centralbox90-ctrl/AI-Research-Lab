from __future__ import annotations

from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class HypothesisEvaluationArtifactEnvelopeFactory:
    """
    Creates envelopes for HypothesisEvaluation artifacts.
    """

    def __init__(
        self,
        *,
        envelope_factory: ResearchArtifactEnvelopeFactory,
    ) -> None:
        if not isinstance(
            envelope_factory,
            ResearchArtifactEnvelopeFactory,
        ):
            raise TypeError(
                "envelope_factory must be a "
                "ResearchArtifactEnvelopeFactory"
            )

        self._envelope_factory = envelope_factory

    def create(
        self,
        *,
        evaluation: HypothesisEvaluation,
        knowledge_revision: (
            KnowledgeRevision | None
        ) = None,
        correlation_id: str | None = None,
    ) -> ResearchArtifactEnvelope:
        if not isinstance(
            evaluation,
            HypothesisEvaluation,
        ):
            raise TypeError(
                "evaluation must be a "
                "HypothesisEvaluation"
            )

        if (
            knowledge_revision is not None
            and not isinstance(
                knowledge_revision,
                KnowledgeRevision,
            )
        ):
            raise TypeError(
                "knowledge_revision must be a "
                "KnowledgeRevision or None"
            )

        presented_evaluation = (
            evaluation.to_dict()
        )
        presented_evaluation["fingerprint"] = (
            evaluation.fingerprint
        )
        payload: dict[str, object] = {
            "evaluation": presented_evaluation,
        }
        source_references = [
            ResearchArtifactSourceReference(
                reference_type=(
                    "hypothesis_evaluation"
                ),
                reference_id=evaluation.id,
                reference_fingerprint=(
                    evaluation.fingerprint
                ),
            )
        ]

        if knowledge_revision is not None:
            payload["knowledge_revision"] = {
                **knowledge_revision.to_dict(),
                "fingerprint": (
                    knowledge_revision.fingerprint
                ),
            }
            source_references.append(
                ResearchArtifactSourceReference(
                    reference_type=(
                        "knowledge_revision"
                    ),
                    reference_id=(
                        knowledge_revision.item.id
                    ),
                    reference_version=(
                        knowledge_revision.item.version
                    ),
                    reference_fingerprint=(
                        knowledge_revision.fingerprint
                    ),
                )
            )

        provenance = dict(
            evaluation.provenance
        )
        provenance.update(
            {
                "hypothesis_evaluation_fingerprint": (
                    evaluation.fingerprint
                ),
                "hypothesis_evaluation_state": (
                    evaluation.state.value
                ),
                "hypothesis_id": (
                    evaluation.hypothesis_id
                ),
            }
        )

        return self._envelope_factory.create(
            artifact_type="hypothesis_evaluation",
            payload_schema_version=(
                2
                if knowledge_revision is not None
                else 1
            ),
            payload=payload,
            provenance=provenance,
            correlation_id=correlation_id,
            source_references=tuple(
                source_references
            ),
        )
