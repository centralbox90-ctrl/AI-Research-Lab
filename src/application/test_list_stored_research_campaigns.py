from typing import Any

from src.application.list_stored_research_campaigns import (
    ListStoredResearchCampaigns,
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


def test_list_stored_research_campaigns_returns_ids() -> None:
    store = FakeSerializedResearchCampaignStore()

    store.save(
        campaign_id="campaign-002",
        serialized_campaign={
            "id": "campaign-002",
        },
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
        },
    )

    use_case = ListStoredResearchCampaigns(
        store=store,
    )

    assert use_case.execute() == [
        "campaign-001",
        "campaign-002",
    ]


def test_list_stored_research_campaigns_returns_empty_list() -> None:
    store = FakeSerializedResearchCampaignStore()

    use_case = ListStoredResearchCampaigns(
        store=store,
    )

    assert use_case.execute() == []
