from pathlib import Path

from src.application.run_and_store_serialized_research_campaign import (
    RunAndStoreSerializedResearchCampaign,
)
from src.research.research_campaign import (
    ResearchCampaign,
)
from src.storage.sqlite_research_campaign_store import (
    SqliteResearchCampaignStore,
)


def test_run_and_store_serialized_campaign_with_sqlite(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "campaigns.db",
    )

    campaign = ResearchCampaign(
        title="SQLite campaign",
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

    loaded = store.get(
        campaign.id,
    )

    assert loaded == result
    assert loaded is not None
    assert loaded["title"] == "SQLite campaign"
    assert loaded["experiment_ids"] == [
        "experiment-001",
    ]