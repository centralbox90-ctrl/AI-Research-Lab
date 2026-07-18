from typing import Any

from src.application.get_stored_research_campaign import (
    GetStoredResearchCampaign,
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
        return list(self.items.keys())


def test_get_stored_research_campaign_returns_campaign() -> None:
    store = FakeSerializedResearchCampaignStore()

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "status": "COMPLETED",
        },
    )

    use_case = GetStoredResearchCampaign(
        store=store,
    )

    result = use_case.execute(
        "campaign-001",
    )

    assert result == {
        "id": "campaign-001",
        "status": "COMPLETED",
    }


def test_get_stored_research_campaign_returns_none_when_missing() -> None:
    store = FakeSerializedResearchCampaignStore()

    use_case = GetStoredResearchCampaign(
        store=store,
    )

    assert use_case.execute(
        "unknown",
    ) is None
