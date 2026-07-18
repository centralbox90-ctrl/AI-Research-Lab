from pathlib import Path

from src.storage.sqlite_research_campaign_store import (
    SqliteResearchCampaignStore,
)


def test_sqlite_research_campaign_store_saves_and_loads_payload(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_campaigns.db"

    store = SqliteResearchCampaignStore(
        db_path=db_path,
    )

    serialized_campaign = {
        "id": "campaign-001",
        "title": "Momentum research",
        "hypothesis_id": "hypothesis-001",
        "experiment_ids": [
            "experiment-001",
            "experiment-002",
        ],
        "status": "COMPLETED",
        "created_at": "2026-07-17T14:00:00",
        "notes": "Campaign completed successfully.",
    }

    store.save(
        campaign_id="campaign-001",
        serialized_campaign=serialized_campaign,
    )

    loaded_campaign = store.get("campaign-001")

    assert loaded_campaign == serialized_campaign
    assert loaded_campaign is not None
    assert loaded_campaign["id"] == "campaign-001"
    assert loaded_campaign["status"] == "COMPLETED"
    assert loaded_campaign["experiment_ids"] == [
        "experiment-001",
        "experiment-002",
    ]


def test_sqlite_research_campaign_store_updates_existing_payload(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "status": "RUNNING",
        },
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "status": "COMPLETED",
        },
    )

    loaded_campaign = store.get("campaign-001")

    assert loaded_campaign is not None
    assert loaded_campaign["status"] == "COMPLETED"


def test_sqlite_research_campaign_store_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    assert store.get("unknown-campaign-id") is None


def test_sqlite_research_campaign_store_lists_campaign_ids(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
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

    assert store.list_campaign_ids() == [
        "campaign-001",
        "campaign-002",
    ]


def test_sqlite_research_campaign_store_lists_no_ids_when_empty(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    assert store.list_campaign_ids() == []
