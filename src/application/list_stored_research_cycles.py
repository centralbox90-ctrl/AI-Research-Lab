from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)


class ListStoredResearchCycles:
    """
    Returns identifiers of research cycles available in persistent storage.
    """

    def __init__(
        self,
        store: SerializedResearchCycleStore,
    ) -> None:
        self.store = store

    def execute(self) -> list[str]:
        return self.store.list_result_ids()