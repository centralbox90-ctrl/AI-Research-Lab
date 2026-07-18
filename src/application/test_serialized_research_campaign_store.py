from typing import Any

from src.application.serialized_research_campaign_store import (
    SerializedResearchCampaignStore,
)


class FakeSerializedResearchCampaignStore:
    def __init__(self) -> None:
        self.items: dict[str, dict[str, Any]] = {}

    def save(
        self,
        campaign_id: str,
        serialized_campaign: dict[str, Any],
    ) -> None:
        self.items[campaign_id] = serialized_campaign

    def get(
        self,
        campaign_id: str,
    ) -> dict[str, Any] | None:
        return self.items.get(campaign_id)

    def list_campaign_ids(self) -> list[str]:
        return sorted(self.items.keys())


def test_serialized_research_campaign_store_contract() -> None:
    store: SerializedResearchCampaignStore = (
        FakeSerializedResearchCampaignStore()
    )

    store.save(
        "campaign-001",
        {
            "id": "campaign-001",
            "status": "COMPLETED",
        },
    )

    assert store.get("campaign-001") == {
        "id": "campaign-001",
        "status": "COMPLETED",
    }

    assert store.list_campaign_ids() == [
        "campaign-001",
    ]