import json
from pathlib import Path

from src.application import (
    ListStoredResearchCampaigns,
)
from src.cli import (
    ListStoredResearchCampaignsCommand,
    ResearchCli,
)
from src.storage import (
    SqliteResearchCampaignStore,
)


def test_research_cli_lists_research_campaigns(
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

    cli = ResearchCli(
        get_research_cycle_command=None,
        list_research_campaigns_command=(
            ListStoredResearchCampaignsCommand(
                list_stored_research_campaigns=(
                    ListStoredResearchCampaigns(
                        store=store,
                    )
                ),
            )
        ),
    )

    from io import StringIO

    stdout = StringIO()

    exit_code = cli.run(
        [
            "list-research-campaigns",
        ],
        stdout=stdout,
    )

    assert exit_code == 0

    assert json.loads(stdout.getvalue()) == [
        "campaign-001",
        "campaign-002",
    ]