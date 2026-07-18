from src.application.serialized_research_campaign_store import (
    SerializedResearchCampaignStore,
)


class ListStoredResearchCampaigns:
    """
    Returns identifiers of research campaigns available in persistent storage.
    """

    def __init__(
        self,
        store: SerializedResearchCampaignStore,
    ) -> None:
        self.store = store

    def execute(self) -> list[str]:
        return self.store.list_campaign_ids()
