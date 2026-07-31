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

        cycle = envelope.payload.get("cycle")

        if not isinstance(cycle, Mapping):
            raise ValueError(
                "market_research_cycle payload must "
                "contain a cycle object"
            )

        result = cycle.get("result")

        if not isinstance(result, Mapping):
            raise ValueError(
                "market_research_cycle payload must "
                "contain a result object"
            )

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