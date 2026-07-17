from typing import Any

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
        return self.store.get(
            result_id,
        )