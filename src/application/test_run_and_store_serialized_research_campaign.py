from pathlib import Path

from src.application.run_and_store_serialized_research_campaign import (
    RunAndStoreSerializedResearchCampaign,
)
from src.application.serialized_research_campaign_store import (
    SerializedResearchCampaignStore,
)
from src.research.research_campaign import (
    ResearchCampaign,
)


class FakeCampaignStore:
    def __init__(self) -> None:
        self.saved_id = None
        self.saved_payload = None

    def save(
        self,
        campaign_id: str,
        serialized_campaign: dict,
    ) -> None:
        self.saved_id = campaign_id
        self.saved_payload = serialized_campaign

    def get(
        self,
        campaign_id: str,
    ):
        return self.saved_payload

    def list_campaign_ids(self) -> list[str]:
        return [
            self.saved_id,
        ]


def test_run_and_store_serialized_campaign() -> None:
    store: SerializedResearchCampaignStore = (
        FakeCampaignStore()
    )

    campaign = ResearchCampaign(
        title="Stored campaign",
        hypothesis_id="hypothesis-001",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    result = (
        RunAndStoreSerializedResearchCampaign(
            store=store,
        )
        .execute(campaign)
    )

    assert result["id"] == campaign.id
    assert result["title"] == "Stored campaign"
    assert result["experiment_ids"] == [
        "experiment-001",
    ]

    assert store.saved_id == campaign.id
    assert store.saved_payload == result