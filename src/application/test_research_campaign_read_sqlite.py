from pathlib import Path

from src.application.get_stored_research_campaign import (
    GetStoredResearchCampaign,
)
from src.application.list_stored_research_campaigns import (
    ListStoredResearchCampaigns,
)
from src.storage.sqlite_research_campaign_store import (
    SqliteResearchCampaignStore,
)


def test_read_research_campaign_from_sqlite(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "campaigns.db",
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "title": "SQLite campaign",
            "status": "COMPLETED",
        },
    )

    get_campaign = GetStoredResearchCampaign(
        store=store,
    )

    result = get_campaign.execute(
        "campaign-001",
    )

    assert result == {
        "id": "campaign-001",
        "title": "SQLite campaign",
        "status": "COMPLETED",
    }


def test_list_research_campaigns_from_sqlite(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "campaigns.db",
    )

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