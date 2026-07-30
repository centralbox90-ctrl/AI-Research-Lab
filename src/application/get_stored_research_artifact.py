from typing import Any

from src.application.research_artifact_envelope import (
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

        return load_research_artifact_envelope(
            stored
        ).to_dict()