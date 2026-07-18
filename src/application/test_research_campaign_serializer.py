from src.application.research_campaign_serializer import (
    ResearchCampaignSerializer,
)
from src.research.research_campaign import (
    ResearchCampaign,
)
from src.research.research_types import (
    ResearchStatus,
)


def test_research_campaign_serializer_serializes_fields() -> None:
    campaign = ResearchCampaign(
        title="Williams campaign",
        hypothesis_id="hypothesis-001",
        notes="test campaign",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    campaign.status = ResearchStatus.COMPLETED

    serialized = ResearchCampaignSerializer().serialize(
        campaign,
    )

    assert serialized["id"] == campaign.id
    assert serialized["title"] == "Williams campaign"
    assert serialized["hypothesis_id"] == (
        "hypothesis-001"
    )
    assert serialized["experiment_ids"] == [
        "experiment-001",
    ]
    assert serialized["status"] == "COMPLETED"
    assert serialized["notes"] == "test campaign"


def test_research_campaign_serializer_is_storage_safe() -> None:
    campaign = ResearchCampaign(
        title="Storage safe",
        hypothesis_id="hypothesis-001",
    )

    serialized = ResearchCampaignSerializer().serialize(
        campaign,
    )

    assert isinstance(
        serialized,
        dict,
    )

    assert not isinstance(
        serialized["created_at"],
        object.__class__,
    )