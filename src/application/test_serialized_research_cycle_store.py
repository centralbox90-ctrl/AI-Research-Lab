from typing import Any

from src.application import SerializedResearchCycleStore


class StoreImplementation:
    def save(
        self,
        result_id: str,
        serialized_cycle: dict[str, Any],
    ) -> None:
        pass

    def get(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        return None

    def list_result_ids(self) -> list[str]:
        return []


def test_serialized_research_cycle_store_defines_storage_boundary() -> None:
    store: SerializedResearchCycleStore = StoreImplementation()

    assert store.get("missing-result") is None
    assert store.list_result_ids() == []