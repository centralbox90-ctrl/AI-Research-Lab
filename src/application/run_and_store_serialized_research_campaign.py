from src.application.research_campaign_serializer import (
    ResearchCampaignSerializer,
)
from src.application.serialized_research_campaign_store import (
    SerializedResearchCampaignStore,
)
from src.research.research_campaign import (
    ResearchCampaign,
)


class RunAndStoreSerializedResearchCampaign:
    """
    Serializes and stores a research campaign.

    Execution of experiments belongs to ResearchEngine.
    This use case only coordinates serialization and persistence.
    """

    def __init__(
        self,
        store: SerializedResearchCampaignStore,
        serializer: ResearchCampaignSerializer | None = None,
    ) -> None:
        self.store = store
        self.serializer = (
            serializer
            or ResearchCampaignSerializer()
        )

    def execute(
        self,
        campaign: ResearchCampaign,
    ) -> dict:
        serialized_campaign = (
            self.serializer.serialize(
                campaign,
            )
        )

        self.store.save(
            campaign_id=campaign.id,
            serialized_campaign=serialized_campaign,
        )

        return serialized_campaign
