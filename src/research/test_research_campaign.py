import pytest
from src.research.research_campaign import (
    ResearchCampaign,
)
from src.research.research_types import (
    ResearchStatus,
)

def test_campaign_cannot_complete_without_experiments() -> None:
    campaign = ResearchCampaign(
        title="Empty campaign",
        hypothesis_id="hypothesis-001",
    )

    campaign.start()

    with pytest.raises(
        ValueError,
        match="without experiments",
    ):
        campaign.complete()

def test_campaign_creates_with_defaults() -> None:
    campaign = ResearchCampaign(
        title="Williams investigation",
        hypothesis_id="hypothesis-001",
    )

    assert campaign.id is not None
    assert campaign.title == "Williams investigation"
    assert campaign.hypothesis_id == "hypothesis-001"
    assert campaign.experiment_ids == []
    assert campaign.status == ResearchStatus.NEW


def test_campaign_lifecycle() -> None:
    campaign = ResearchCampaign(
        title="Lifecycle test",
        hypothesis_id="hypothesis-001",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    assert campaign.status == ResearchStatus.NEW

    campaign.start()

    assert campaign.status == ResearchStatus.RUNNING

    campaign.complete()

    assert campaign.status == ResearchStatus.COMPLETED

def test_campaign_cannot_complete_from_new() -> None:
    campaign = ResearchCampaign(
        title="Invalid transition",
        hypothesis_id="hypothesis-001",
    )

    with pytest.raises(
        ValueError,
        match="RUNNING",
    ):
        campaign.complete()

def test_campaign_adds_experiment_once() -> None:
    campaign = ResearchCampaign(
        title="Campaign",
        hypothesis_id="hypothesis-001",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    assert campaign.experiment_ids == [
        "experiment-001",
    ]


def test_campaign_summary_contains_state() -> None:
    campaign = ResearchCampaign(
        title="Campaign",
        hypothesis_id="hypothesis-001",
    )

    campaign.add_experiment(
        "experiment-001",
    )

    summary = campaign.summary()

    assert "Campaign" in summary
    assert "hypothesis-001" in summary
    assert "Experiments: 1" in summary
    assert "Status: NEW" in summary
