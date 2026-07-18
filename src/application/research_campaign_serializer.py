from typing import Any

from src.research.research_campaign import (
    ResearchCampaign,
)


class ResearchCampaignSerializer:
    """
    Serializes ResearchCampaign into application-safe data.

    The serializer does not modify the domain model.
    It returns only dictionaries suitable for storage adapters.
    """

    def serialize(
        self,
        campaign: ResearchCampaign,
    ) -> dict[str, Any]:
        return {
            "id": campaign.id,
            "title": campaign.title,
            "hypothesis_id": campaign.hypothesis_id,
            "experiment_ids": list(
                campaign.experiment_ids,
            ),
            "status": str(
                campaign.status,
            ),
            "created_at": (
                campaign.created_at.isoformat()
            ),
            "notes": campaign.notes,
        }