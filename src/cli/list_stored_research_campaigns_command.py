import json

from src.application import ListStoredResearchCampaigns


class ListStoredResearchCampaignsCommand:
    """
    CLI command handler for listing persistent research-campaign IDs.
    """

    def __init__(
        self,
        list_stored_research_campaigns: ListStoredResearchCampaigns,
    ) -> None:
        self.list_stored_research_campaigns = (
            list_stored_research_campaigns
        )

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        campaign_ids = (
            self.list_stored_research_campaigns.execute()
        )

        return json.dumps(
            campaign_ids,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )
