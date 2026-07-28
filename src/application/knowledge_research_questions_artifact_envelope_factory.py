from __future__ import annotations

from src.application.generate_research_questions_from_knowledge_repositories import (
    KnowledgeResearchQuestionsResult,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
)


class KnowledgeResearchQuestionsArtifactEnvelopeFactory:
    """
    Creates envelopes for repository-backed research questions.
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
        result: KnowledgeResearchQuestionsResult,
        correlation_id: str | None = None,
    ) -> ResearchArtifactEnvelope:
        if not isinstance(
            result,
            KnowledgeResearchQuestionsResult,
        ):
            raise TypeError(
                "result must be a "
                "KnowledgeResearchQuestionsResult"
            )

        snapshot = result.snapshot
        snapshot_fingerprint = (
            snapshot.fingerprint
        )
        payload = {
            "snapshot": snapshot.to_dict(),
            "snapshot_fingerprint": (
                snapshot_fingerprint
            ),
            "question_count": len(
                result.questions
            ),
            "questions": [
                question.to_dict()
                for question in result.questions
            ],
        }
        provenance = {
            "knowledge_snapshot_fingerprint": (
                snapshot_fingerprint
            ),
            "knowledge_item_count": len(
                snapshot.items
            ),
            "knowledge_relation_count": len(
                snapshot.relations
            ),
        }

        return self._envelope_factory.create(
            artifact_type=(
                "knowledge_research_questions"
            ),
            payload_schema_version=1,
            payload=payload,
            provenance=provenance,
            correlation_id=correlation_id,
            source_references=(
                ResearchArtifactSourceReference(
                    reference_type=(
                        "knowledge_graph_snapshot"
                    ),
                    reference_id=(
                        snapshot_fingerprint
                    ),
                    reference_fingerprint=(
                        snapshot_fingerprint
                    ),
                ),
            ),
        )
