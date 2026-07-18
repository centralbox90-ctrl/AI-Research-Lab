from src.application import GetStoredResearchCampaign
from src.cli.research_campaign_json import (
    ResearchCampaignJsonPresenter,
)


class GetStoredResearchCampaignCommand:
    """
    CLI command handler for retrieving persistent research-campaign data.

    The handler receives application-safe dictionaries from the
    application layer and renders them as JSON.
    """

    def __init__(
        self,
        get_stored_research_campaign: GetStoredResearchCampaign,
        presenter: ResearchCampaignJsonPresenter | None = None,
    ) -> None:
        self.get_stored_research_campaign = (
            get_stored_research_campaign
        )
        self.presenter = (
            presenter or ResearchCampaignJsonPresenter()
        )

    def execute(
        self,
        campaign_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        stored_campaign = (
            self.get_stored_research_campaign.execute(
                campaign_id,
            )
        )

        if stored_campaign is None:
            return None

        return self.presenter.render(
            stored_campaign,
            indent=indent,
        )