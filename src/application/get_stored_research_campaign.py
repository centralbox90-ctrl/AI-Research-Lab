from typing import Any

from src.application.serialized_research_campaign_store import (
    SerializedResearchCampaignStore,
)


class GetStoredResearchCampaign:
    """
    Returns serialized research campaign data from storage.
    """

    def __init__(
        self,
        store: SerializedResearchCampaignStore,
    ) -> None:
        self.store = store

    def execute(
        self,
        campaign_id: str,
    ) -> dict[str, Any] | None:
        return self.store.get(
            campaign_id,
        )
