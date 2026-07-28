from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from src.application.generate_research_questions_from_knowledge_repositories import (
    KnowledgeResearchQuestionsResult,
)
from src.application.knowledge_graph_snapshot_loader import (
    KnowledgeGraphSnapshotLoader,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactSourceReference,
    load_research_artifact_envelope,
)
from src.research.question import ResearchQuestion
from src.research.research_types import ResearchStatus


@dataclass(frozen=True, slots=True)
class LoadedKnowledgeResearchQuestionsArtifact:
    """
    Typed result of loading one Knowledge-question envelope.
    """

    result: KnowledgeResearchQuestionsResult
    envelope: ResearchArtifactEnvelope

    def __post_init__(self) -> None:
        if not isinstance(
            self.result,
            KnowledgeResearchQuestionsResult,
        ):
            raise TypeError(
                "result must be a "
                "KnowledgeResearchQuestionsResult"
            )

        if not isinstance(
            self.envelope,
            ResearchArtifactEnvelope,
        ):
            raise TypeError(
                "envelope must be a "
                "ResearchArtifactEnvelope"
            )


class KnowledgeResearchQuestionsArtifactLoader:
    """
    Loads a complete Knowledge-question envelope.
    """

    _PAYLOAD_FIELDS = {
        "snapshot",
        "snapshot_fingerprint",
        "question_count",
        "questions",
    }
    _QUESTION_FIELDS = {
        "id",
        "statement",
        "description",
        "created_at",
        "status",
    }

    def __init__(
        self,
        snapshot_loader: (
            KnowledgeGraphSnapshotLoader | None
        ) = None,
    ) -> None:
        if (
            snapshot_loader is not None
            and not isinstance(
                snapshot_loader,
                KnowledgeGraphSnapshotLoader,
            )
        ):
            raise TypeError(
                "snapshot_loader must be a "
                "KnowledgeGraphSnapshotLoader or None"
            )

        self._snapshot_loader = (
            snapshot_loader
            or KnowledgeGraphSnapshotLoader()
        )

    def load(
        self,
        serialized: Mapping[str, object],
    ) -> LoadedKnowledgeResearchQuestionsArtifact:
        if not isinstance(serialized, Mapping):
            raise TypeError(
                "serialized artifact must be a mapping"
            )

        envelope = load_research_artifact_envelope(
            serialized
        )

        if envelope.artifact_type != (
            "knowledge_research_questions"
        ):
            raise ValueError(
                "artifact_type must be "
                "knowledge_research_questions"
            )

        if envelope.payload_schema_version != 1:
            raise ValueError(
                "payload_schema_version must be 1"
            )

        serialized_envelope = envelope.to_dict()
        payload = self._require_object(
            serialized_envelope["payload"],
            label="payload",
        )
        self._validate_fields(
            payload,
            expected=self._PAYLOAD_FIELDS,
            label="payload",
        )

        snapshot_payload = self._require_object(
            payload["snapshot"],
            label="payload.snapshot",
        )
        snapshot = self._snapshot_loader.from_dict(
            snapshot_payload
        )
        snapshot_fingerprint = payload[
            "snapshot_fingerprint"
        ]

        if (
            not isinstance(
                snapshot_fingerprint,
                str,
            )
            or snapshot_fingerprint
            != snapshot.fingerprint
        ):
            raise ValueError(
                "snapshot_fingerprint does not "
                "match snapshot"
            )

        question_count = payload[
            "question_count"
        ]

        if (
            not isinstance(question_count, int)
            or isinstance(question_count, bool)
            or question_count < 0
        ):
            raise ValueError(
                "question_count must be a "
                "non-negative integer"
            )

        question_payloads = payload["questions"]

        if not isinstance(question_payloads, list):
            raise ValueError(
                "questions must be an array"
            )

        if question_count != len(
            question_payloads
        ):
            raise ValueError(
                "question_count does not match "
                "questions"
            )

        questions = tuple(
            self._load_question(
                question_payload,
                index=index,
            )
            for index, question_payload
            in enumerate(question_payloads)
        )
        result = KnowledgeResearchQuestionsResult(
            snapshot=snapshot,
            questions=questions,
        )

        self._validate_source_reference(
            envelope=envelope,
            snapshot_fingerprint=(
                snapshot.fingerprint
            ),
        )

        return LoadedKnowledgeResearchQuestionsArtifact(
            result=result,
            envelope=envelope,
        )

    def _load_question(
        self,
        value: object,
        *,
        index: int,
    ) -> ResearchQuestion:
        label = f"questions[{index}]"
        serialized = self._require_object(
            value,
            label=label,
        )
        self._validate_fields(
            serialized,
            expected=self._QUESTION_FIELDS,
            label=label,
        )
        created_at_value = serialized[
            "created_at"
        ]

        if not isinstance(created_at_value, str):
            raise ValueError(
                f"{label}.created_at must be a string"
            )

        try:
            created_at = datetime.fromisoformat(
                created_at_value
            )
        except ValueError as error:
            raise ValueError(
                f"{label}.created_at is invalid"
            ) from error

        status_value = serialized["status"]

        try:
            status = ResearchStatus(status_value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{label}.status is unsupported"
            ) from error

        try:
            return ResearchQuestion(
                id=serialized["id"],
                statement=serialized["statement"],
                description=serialized[
                    "description"
                ],
                created_at=created_at,
                status=status,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{label} is invalid: {error}"
            ) from error

    @staticmethod
    def _validate_source_reference(
        *,
        envelope: ResearchArtifactEnvelope,
        snapshot_fingerprint: str,
    ) -> None:
        expected = (
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
        )

        if envelope.source_references != expected:
            raise ValueError(
                "source_references must identify "
                "the exact Knowledge snapshot"
            )

    @staticmethod
    def _require_object(
        value: object,
        *,
        label: str,
    ) -> dict[str, object]:
        if not isinstance(value, dict):
            raise ValueError(
                f"{label} must be an object"
            )

        if any(
            not isinstance(key, str)
            for key in value
        ):
            raise ValueError(
                f"{label} field names must be strings"
            )

        return value

    @staticmethod
    def _validate_fields(
        payload: dict[str, object],
        *,
        expected: set[str],
        label: str,
    ) -> None:
        fields = set(payload)
        missing = sorted(expected - fields)
        unknown = sorted(fields - expected)

        if missing:
            raise ValueError(
                f"{label} missing fields: "
                + ", ".join(missing)
            )

        if unknown:
            raise ValueError(
                f"{label} unknown fields: "
                + ", ".join(unknown)
            )
