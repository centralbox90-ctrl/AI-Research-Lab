from typing import Any, Protocol


class SerializedResearchCycleStore(Protocol):
    """
    Persistence boundary for serialized research cycles.

    Implementations store application-safe dictionaries and do not
    reconstruct research domain objects.
    """

    def save(
        self,
        result_id: str,
        serialized_cycle: dict[str, Any],
    ) -> None:
        """
        Save serialized research-cycle data.
        """

    def get(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        """
        Return serialized research-cycle data by result ID.
        """

    def list_result_ids(self) -> list[str]:
        """
        Return IDs of all stored research cycles.
        """