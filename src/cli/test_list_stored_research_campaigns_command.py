import json
from pathlib import Path

from src.application import ListStoredResearchCampaigns
from src.cli import ListStoredResearchCampaignsCommand
from src.storage import SqliteResearchCampaignStore


def test_list_stored_research_campaigns_command_returns_json_ids(
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

    command = ListStoredResearchCampaignsCommand(
        list_stored_research_campaigns=(
            ListStoredResearchCampaigns(
                store=store,
            )
        ),
    )

    rendered = command.execute()

    assert json.loads(rendered) == [
        "campaign-001",
        "campaign-002",
    ]


def test_list_stored_research_campaigns_command_returns_empty_json_array(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    command = ListStoredResearchCampaignsCommand(
        list_stored_research_campaigns=(
            ListStoredResearchCampaigns(
                store=store,
            )
        ),
    )

    assert json.loads(command.execute()) == []


def test_list_stored_research_campaigns_command_supports_compact_json(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
        },
    )

    command = ListStoredResearchCampaignsCommand(
        list_stored_research_campaigns=(
            ListStoredResearchCampaigns(
                store=store,
            )
        ),
    )

    rendered = command.execute(
        indent=None,
    )

    assert rendered == '["campaign-001"]'
    assert "\n" not in rendered
