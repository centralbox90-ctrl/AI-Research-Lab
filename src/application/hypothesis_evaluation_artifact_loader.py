from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    is_research_artifact_envelope,
    load_research_artifact_envelope,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


@dataclass(frozen=True, slots=True)
class LoadedHypothesisEvaluationArtifact:
    """Typed result of loading one evaluation artifact."""

    evaluation: HypothesisEvaluation
    knowledge_revision: KnowledgeRevision | None
    envelope: ResearchArtifactEnvelope | None

    def __post_init__(self) -> None:
        if not isinstance(
            self.evaluation,
            HypothesisEvaluation,
        ):
            raise TypeError(
                "evaluation must be a "
                "HypothesisEvaluation"
            )

        if (
            self.knowledge_revision is not None
            and not isinstance(
                self.knowledge_revision,
                KnowledgeRevision,
            )
        ):
            raise TypeError(
                "knowledge_revision must be a "
                "KnowledgeRevision or None"
            )

        if (
            self.envelope is not None
            and not isinstance(
                self.envelope,
                ResearchArtifactEnvelope,
            )
        ):
            raise TypeError(
                "envelope must be a "
                "ResearchArtifactEnvelope or None"
            )


class HypothesisEvaluationArtifactLoader:
    """
    Loads legacy and enveloped HypothesisEvaluation artifacts.
    """

    def load(
        self,
        serialized: Mapping[str, object],
    ) -> LoadedHypothesisEvaluationArtifact:
        if not isinstance(serialized, Mapping):
            raise TypeError(
                "serialized artifact must be a mapping"
            )

        envelope: ResearchArtifactEnvelope | None

        if is_research_artifact_envelope(
            serialized
        ):
            envelope = load_research_artifact_envelope(
                serialized
            )

            if envelope.artifact_type != (
                "hypothesis_evaluation"
            ):
                raise ValueError(
                    "artifact_type must be "
                    "hypothesis_evaluation"
                )

            payload_schema_version = (
                envelope.payload_schema_version
            )
            payload = envelope.payload
        else:
            envelope = None
            payload_schema_version, payload = (
                self._load_legacy_boundary(
                    serialized
                )
            )

        if payload_schema_version not in (1, 2):
            raise ValueError(
                "payload schema version must be 1 or 2"
            )

        required_payload_fields = {
            "evaluation",
        }

        if payload_schema_version == 2:
            required_payload_fields.add(
                "knowledge_revision"
            )

        payload_mapping = self._require_fields(
            payload,
            required=required_payload_fields,
            label="hypothesis evaluation payload",
        )
        evaluation = self._load_evaluation(
            payload_mapping["evaluation"]
        )
        knowledge_revision = None

        if payload_schema_version == 2:
            knowledge_revision = (
                self._load_knowledge_revision(
                    payload_mapping[
                        "knowledge_revision"
                    ]
                )
            )

        return LoadedHypothesisEvaluationArtifact(
            evaluation=evaluation,
            knowledge_revision=knowledge_revision,
            envelope=envelope,
        )

    def _load_legacy_boundary(
        self,
        serialized: Mapping[str, object],
    ) -> tuple[int, Mapping[str, object]]:
        if serialized.get("artifact_type") != (
            "hypothesis_evaluation"
        ):
            raise ValueError(
                "artifact_type must be "
                "hypothesis_evaluation"
            )

        artifact_version = serialized.get(
            "artifact_version"
        )

        if artifact_version == 1:
            boundary = self._require_fields(
                serialized,
                required={
                    "artifact_type",
                    "artifact_version",
                    "evaluation",
                },
                label=(
                    "legacy hypothesis evaluation artifact"
                ),
            )

            return (
                1,
                {
                    "evaluation": (
                        boundary["evaluation"]
                    ),
                },
            )

        if artifact_version == 2:
            boundary = self._require_fields(
                serialized,
                required={
                    "artifact_type",
                    "artifact_version",
                    "evaluation",
                    "knowledge_revision",
                },
                label=(
                    "legacy hypothesis evaluation artifact"
                ),
            )

            return (
                2,
                {
                    "evaluation": (
                        boundary["evaluation"]
                    ),
                    "knowledge_revision": (
                        boundary[
                            "knowledge_revision"
                        ]
                    ),
                },
            )

        raise ValueError(
            "artifact_version must be 1 or 2"
        )

    def _load_evaluation(
        self,
        value: object,
    ) -> HypothesisEvaluation:
        serialized = self._require_fields(
            value,
            required={
                "schema_version",
                "id",
                "hypothesis_id",
                "state",
                "confidence",
                "finding_refs",
                "rationale",
                "limitations",
                "provenance",
                "fingerprint",
            },
            label="evaluation",
        )

        if serialized["schema_version"] != 1:
            raise ValueError(
                "evaluation schema_version must be 1"
            )

        state_value = serialized["state"]

        try:
            state = HypothesisEvaluationState(
                state_value
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "evaluation state is unsupported"
            ) from error

        evaluation = HypothesisEvaluation(
            id=serialized["id"],
            hypothesis_id=serialized[
                "hypothesis_id"
            ],
            state=state,
            confidence=serialized["confidence"],
            finding_refs=self._load_text_tuple(
                serialized["finding_refs"],
                label="evaluation finding_refs",
            ),
            rationale=self._load_text_tuple(
                serialized["rationale"],
                label="evaluation rationale",
            ),
            limitations=self._load_text_tuple(
                serialized["limitations"],
                label="evaluation limitations",
            ),
            provenance=self._load_provenance(
                serialized["provenance"],
                label="evaluation provenance",
            ),
        )

        if serialized["fingerprint"] != (
            evaluation.fingerprint
        ):
            raise ValueError(
                "evaluation fingerprint does not match"
            )

        return evaluation

    def _load_knowledge_revision(
        self,
        value: object,
    ) -> KnowledgeRevision:
        serialized = self._require_fields(
            value,
            required={
                "schema_version",
                "item",
                "item_fingerprint",
                "valid_from",
                "change_reason",
                "supersedes_version",
                "fingerprint",
            },
            label="knowledge_revision",
        )

        if serialized["schema_version"] != 1:
            raise ValueError(
                "knowledge_revision schema_version "
                "must be 1"
            )

        item = self._load_knowledge_item(
            serialized["item"]
        )

        if serialized["item_fingerprint"] != (
            item.fingerprint
        ):
            raise ValueError(
                "knowledge item fingerprint "
                "does not match"
            )

        valid_from_value = serialized[
            "valid_from"
        ]

        if not isinstance(valid_from_value, str):
            raise TypeError(
                "knowledge_revision valid_from "
                "must be a string"
            )

        try:
            valid_from = datetime.fromisoformat(
                valid_from_value.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as error:
            raise ValueError(
                "knowledge_revision valid_from "
                "is invalid"
            ) from error

        revision = KnowledgeRevision(
            item=item,
            valid_from=valid_from,
            change_reason=serialized[
                "change_reason"
            ],
            supersedes_version=serialized[
                "supersedes_version"
            ],
        )

        if serialized["fingerprint"] != (
            revision.fingerprint
        ):
            raise ValueError(
                "knowledge revision fingerprint "
                "does not match"
            )

        return revision

    def _load_knowledge_item(
        self,
        value: object,
    ) -> KnowledgeItem:
        serialized = self._require_fields(
            value,
            required={
                "schema_version",
                "id",
                "statement",
                "confidence",
                "applicability",
                "limitations",
                "supporting_findings",
                "version",
                "provenance",
            },
            label="knowledge item",
        )

        if serialized["schema_version"] != 1:
            raise ValueError(
                "knowledge item schema_version "
                "must be 1"
            )

        return KnowledgeItem(
            id=serialized["id"],
            statement=serialized["statement"],
            confidence=serialized["confidence"],
            applicability=self._load_text_tuple(
                serialized["applicability"],
                label=(
                    "knowledge item applicability"
                ),
            ),
            limitations=self._load_text_tuple(
                serialized["limitations"],
                label=(
                    "knowledge item limitations"
                ),
            ),
            supporting_findings=(
                self._load_text_tuple(
                    serialized[
                        "supporting_findings"
                    ],
                    label=(
                        "knowledge item "
                        "supporting_findings"
                    ),
                )
            ),
            version=serialized["version"],
            provenance=self._load_provenance(
                serialized["provenance"],
                label=(
                    "knowledge item provenance"
                ),
            ),
        )

    @staticmethod
    def _require_fields(
        value: object,
        *,
        required: set[str],
        label: str,
    ) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError(
                f"{label} must be a mapping"
            )

        keys = set(value.keys())

        if any(
            not isinstance(key, str)
            for key in keys
        ):
            raise TypeError(
                f"{label} keys must be strings"
            )

        missing = sorted(
            required - keys
        )

        if missing:
            raise ValueError(
                f"{label} missing fields: "
                + ", ".join(missing)
            )

        unknown = sorted(
            keys - required
        )

        if unknown:
            raise ValueError(
                f"{label} unknown fields: "
                + ", ".join(unknown)
            )

        return value

    @staticmethod
    def _load_text_tuple(
        value: object,
        *,
        label: str,
    ) -> tuple[str, ...]:
        if not isinstance(
            value,
            (list, tuple),
        ):
            raise TypeError(
                f"{label} must be an array"
            )

        return tuple(value)

    @staticmethod
    def _load_provenance(
        value: object,
        *,
        label: str,
    ) -> tuple[tuple[str, str], ...]:
        if not isinstance(value, Mapping):
            raise TypeError(
                f"{label} must be a mapping"
            )

        return tuple(
            value.items()
        )
