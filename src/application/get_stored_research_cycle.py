from typing import Any

from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)


class GetStoredResearchCycle:
    """
    Retrieves a serialized research cycle from persistent storage.

    The use case returns application-safe data without reconstructing
    research domain objects.
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
        return self.store.get(result_id)