from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
    StoredResearchArtifactIntegrityError,
)
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
        self._artifact_reader = (
            GetStoredResearchArtifact(
                store=store,
            )
        )

    def execute(self) -> list[str]:
        result_ids = self.store.list_result_ids()

        for result_id in result_ids:
            artifact = self._artifact_reader.execute(
                result_id
            )

            if artifact is None:
                raise StoredResearchArtifactIntegrityError(
                    result_id=result_id,
                    reason=(
                        "listed research artifact "
                        "is missing"
                    ),
                )

        return result_ids