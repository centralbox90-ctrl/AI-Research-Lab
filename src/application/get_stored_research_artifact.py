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
            self._validate_legacy_storage_identity(
                result_id=result_id,
                stored=stored,
            )
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

    @staticmethod
    def _validate_legacy_storage_identity(
        *,
        result_id: str,
        stored: Mapping[str, object],
    ) -> None:
        cycle_fields = {
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
        flat_metadata_fields = {
            "artifact_version",
            "artifact_type",
        }

        if "cycle" in stored:
            allowed_artifact_fields = {
                "artifact_version",
                "specification",
                "cycle",
                "research_environment",
                "metadata",
                "lineage",
                "comparisons",
                "history",
            }
            unknown_artifact_fields = sorted(
                set(stored) - allowed_artifact_fields
            )

            if unknown_artifact_fields:
                raise ValueError(
                    "legacy market research artifact "
                    "has unknown fields: "
                    + ", ".join(
                        unknown_artifact_fields
                    )
                )

            for field_name in (
                "specification",
                "research_environment",
                "metadata",
                "lineage",
            ):
                if (
                    field_name in stored
                    and not isinstance(
                        stored[field_name],
                        Mapping,
                    )
                ):
                    raise ValueError(
                        "legacy market research artifact "
                        f"field {field_name} must be "
                        "an object"
                    )

            if "comparisons" in stored:
                comparisons = stored["comparisons"]

                if (
                    not isinstance(
                        comparisons,
                        (list, tuple),
                    )
                    or any(
                        not isinstance(
                            comparison,
                            Mapping,
                        )
                        for comparison in comparisons
                    )
                ):
                    raise ValueError(
                        "legacy market research "
                        "comparisons must be an array "
                        "of objects"
                    )

            if "history" in stored:
                history = stored["history"]

                if (
                    not isinstance(
                        history,
                        (list, tuple),
                    )
                    or any(
                        not isinstance(
                            event,
                            Mapping,
                        )
                        for event in history
                    )
                ):
                    raise ValueError(
                        "legacy market research history "
                        "must be an array of objects"
                    )

            cycle = stored["cycle"]
        else:
            unknown_flat_fields = sorted(
                set(stored)
                - cycle_fields
                - flat_metadata_fields
            )

            if unknown_flat_fields:
                raise ValueError(
                    "legacy research cycle has "
                    "unknown fields: "
                    + ", ".join(unknown_flat_fields)
                )

            cycle = stored

        if not isinstance(cycle, Mapping):
            raise ValueError(
                "legacy research cycle must be "
                "an object"
            )

        unknown_cycle_fields = sorted(
            set(cycle)
            - cycle_fields
            - flat_metadata_fields
        )

        if unknown_cycle_fields:
            raise ValueError(
                "legacy research cycle has "
                "unknown fields: "
                + ", ".join(unknown_cycle_fields)
            )

        for field_name in sorted(
            set(cycle) & cycle_fields
        ):
            if not isinstance(
                cycle[field_name],
                Mapping,
            ):
                raise ValueError(
                    "legacy research cycle field "
                    f"{field_name} must be an object"
                )

        if "artifact_version" in stored:
            artifact_version = stored[
                "artifact_version"
            ]

            if (
                not isinstance(artifact_version, int)
                or isinstance(artifact_version, bool)
                or artifact_version != 1
            ):
                raise ValueError(
                    "legacy market research "
                    "artifact_version must be 1"
                )

        if "artifact_type" in stored:
            artifact_type = stored["artifact_type"]

            if (
                not isinstance(artifact_type, str)
                or not artifact_type.strip()
            ):
                raise ValueError(
                    "legacy research artifact_type "
                    "must be a non-empty string"
                )

        result = cycle.get("result")

        if not isinstance(result, Mapping):
            raise ValueError(
                "legacy research cycle must contain "
                "a result object"
            )

        payload_result_id = result.get("id")

        if (
            not isinstance(payload_result_id, str)
            or not payload_result_id.strip()
        ):
            raise ValueError(
                "legacy research cycle result id "
                "must be a non-empty string"
            )

        if payload_result_id != result_id:
            raise ValueError(
                "legacy research cycle result id does "
                "not match storage key"
            )
