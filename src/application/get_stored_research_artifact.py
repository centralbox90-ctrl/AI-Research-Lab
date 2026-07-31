from collections.abc import Mapping
from typing import Any

from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    is_research_artifact_envelope,
    load_research_artifact_envelope,
)
from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)


class GetStoredResearchArtifact:
    """
    Retrieves a stored research artifact from persistent storage.

    The use case returns application-safe artifact dictionaries.
    It does not reconstruct research domain objects.
    """

    def __init__(
        self,
        store: SerializedResearchCycleStore,
    ) -> None:
        self.store = store

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        stored = self.store.get(
            result_id,
        )

        if stored is None:
            return None

        if not is_research_artifact_envelope(
            stored
        ):
            return stored

        envelope = load_research_artifact_envelope(
            stored
        )

        self._validate_storage_identity(
            result_id=result_id,
            envelope=envelope,
        )

        return envelope.to_dict()

    @staticmethod
    def _validate_storage_identity(
        *,
        result_id: str,
        envelope: ResearchArtifactEnvelope,
    ) -> None:
        if envelope.artifact_type != (
            "market_research_cycle"
        ):
            return

        if envelope.payload_schema_version != 1:
            raise ValueError(
                "market_research_cycle "
                "payload_schema_version must be 1"
            )

        payload = envelope.payload
        required_payload_fields = {
            "artifact_version",
            "specification",
            "cycle",
        }
        optional_payload_fields = {
            "research_environment",
            "metadata",
            "lineage",
            "comparisons",
        }
        payload_fields = set(payload)
        missing_payload_fields = sorted(
            required_payload_fields - payload_fields
        )
        unknown_payload_fields = sorted(
            payload_fields
            - required_payload_fields
            - optional_payload_fields
        )

        if missing_payload_fields:
            raise ValueError(
                "market_research_cycle payload is "
                "missing fields: "
                + ", ".join(missing_payload_fields)
            )

        if unknown_payload_fields:
            raise ValueError(
                "market_research_cycle payload has "
                "unknown fields: "
                + ", ".join(unknown_payload_fields)
            )

        artifact_version = payload["artifact_version"]

        if (
            not isinstance(artifact_version, int)
            or isinstance(artifact_version, bool)
            or artifact_version
            != envelope.payload_schema_version
        ):
            raise ValueError(
                "market_research_cycle artifact_version "
                "must match payload_schema_version"
            )

        specification = payload["specification"]

        if not isinstance(specification, Mapping):
            raise ValueError(
                "market_research_cycle specification "
                "must be an object"
            )

        cycle = payload["cycle"]

        if not isinstance(cycle, Mapping):
            raise ValueError(
                "market_research_cycle cycle must "
                "be an object"
            )

        required_cycle_fields = {
            "result",
            "evaluation",
            "statistical_evaluation",
            "robustness_evaluation",
            "contradiction_evaluation",
            "evidence_strength_evaluation",
            "hypothesis_decision",
            "next_experiment_selection",
            "evidence",
            "analysis",
            "conclusion",
            "knowledge",
        }
        cycle_fields = set(cycle)
        missing_cycle_fields = sorted(
            required_cycle_fields - cycle_fields
        )
        unknown_cycle_fields = sorted(
            cycle_fields - required_cycle_fields
        )

        if missing_cycle_fields:
            raise ValueError(
                "market_research_cycle cycle is "
                "missing fields: "
                + ", ".join(missing_cycle_fields)
            )

        if unknown_cycle_fields:
            raise ValueError(
                "market_research_cycle cycle has "
                "unknown fields: "
                + ", ".join(unknown_cycle_fields)
            )

        for field_name in sorted(
            required_cycle_fields
        ):
            if not isinstance(
                cycle[field_name],
                Mapping,
            ):
                raise ValueError(
                    "market_research_cycle cycle field "
                    f"{field_name} must be an object"
                )

        for field_name in (
            "research_environment",
            "metadata",
            "lineage",
        ):
            if (
                field_name in payload
                and not isinstance(
                    payload[field_name],
                    Mapping,
                )
            ):
                raise ValueError(
                    "market_research_cycle payload field "
                    f"{field_name} must be an object"
                )

        if "comparisons" in payload:
            comparisons = payload["comparisons"]

            if (
                not isinstance(comparisons, tuple)
                or any(
                    not isinstance(
                        comparison,
                        Mapping,
                    )
                    for comparison in comparisons
                )
            ):
                raise ValueError(
                    "market_research_cycle comparisons "
                    "must be an array of objects"
                )

        result = cycle["result"]
        payload_result_id = result.get("id")

        if (
            not isinstance(payload_result_id, str)
            or not payload_result_id.strip()
        ):
            raise ValueError(
                "market_research_cycle result id must "
                "be a non-empty string"
            )

        if payload_result_id != result_id:
            raise ValueError(
                "market_research_cycle result id does "
                "not match storage key"
            )
