import json
from pathlib import Path

from src.application import GetStoredResearchCampaign
from src.cli import GetStoredResearchCampaignCommand
from src.storage import SqliteResearchCampaignStore


def test_get_stored_research_campaign_command_returns_json(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "title": "Test campaign",
            "status": "COMPLETED",
        },
    )

    command = GetStoredResearchCampaignCommand(
        get_stored_research_campaign=(
            GetStoredResearchCampaign(
                store=store,
            )
        ),
    )

    rendered = command.execute(
        "campaign-001",
    )

    assert rendered is not None

    assert json.loads(rendered) == {
        "id": "campaign-001",
        "status": "COMPLETED",
        "title": "Test campaign",
    }


def test_get_stored_research_campaign_command_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "research_campaigns.db",
    )

    command = GetStoredResearchCampaignCommand(
        get_stored_research_campaign=(
            GetStoredResearchCampaign(
                store=store,
            )
        ),
    )

    assert command.execute(
        "unknown-campaign",
    ) is None


def test_get_stored_research_campaign_command_supports_compact_json(
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

    command = GetStoredResearchCampaignCommand(
        get_stored_research_campaign=(
            GetStoredResearchCampaign(
                store=store,
            )
        ),
    )

    rendered = command.execute(
        "campaign-001",
        indent=None,
    )

    assert rendered == '{"id": "campaign-001"}'
    assert "\n" not in rendered