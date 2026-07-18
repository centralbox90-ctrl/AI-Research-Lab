import json
from io import StringIO
from pathlib import Path

from src.application import GetStoredResearchCampaign
from src.cli import (
    GetStoredResearchCampaignCommand,
    ResearchCli,
)
from src.storage import SqliteResearchCampaignStore


def test_research_cli_get_research_campaign(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "campaigns.db",
    )

    store.save(
        campaign_id="campaign-001",
        serialized_campaign={
            "id": "campaign-001",
            "title": "CLI campaign",
        },
    )

    cli = ResearchCli(
        get_research_cycle_command=None,
        get_research_campaign_command=(
            GetStoredResearchCampaignCommand(
                get_stored_research_campaign=(
                    GetStoredResearchCampaign(
                        store=store,
                    )
                ),
            )
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-research-campaign",
            "campaign-001",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0

    assert json.loads(stdout.getvalue()) == {
        "id": "campaign-001",
        "title": "CLI campaign",
    }


def test_research_cli_get_missing_campaign(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCampaignStore(
        db_path=tmp_path / "campaigns.db",
    )

    cli = ResearchCli(
        get_research_cycle_command=None,
        get_research_campaign_command=(
            GetStoredResearchCampaignCommand(
                get_stored_research_campaign=(
                    GetStoredResearchCampaign(
                        store=store,
                    )
                ),
            )
        ),
    )

    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-research-campaign",
            "missing",
        ],
        stderr=stderr,
    )

    assert exit_code == 1
    assert "Research campaign not found" in stderr.getvalue()