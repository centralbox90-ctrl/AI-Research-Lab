import json
from io import StringIO
from pathlib import Path

from src.application.campaign_design_loader import (
    CampaignDesignLoader,
)
from src.application.market_experiment_registration_loader import (
    MarketExperimentRegistrationLoader,
)
from src.cli.main import main
from src.research.research_planner import (
    ResearchPlanner,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_DESIGN_PATH = (
    _REPOSITORY_ROOT
    / "examples"
    / "campaign_design.json"
)
_REGISTRATION_PATH = (
    _REPOSITORY_ROOT
    / "examples"
    / "campaign_registrations.json"
)


def test_campaign_example_contracts_are_consistent(
) -> None:
    design = CampaignDesignLoader().load(
        _DESIGN_PATH
    )
    plan = ResearchPlanner().plan(design)

    resolver = MarketExperimentRegistrationLoader().load(
        _REGISTRATION_PATH,
        plan=plan,
    )

    assert len(plan.experiment_specifications) == 1

    planned = plan.experiment_specifications[0]
    resolved = resolver.resolve(planned)

    assert resolved.symbol == planned.instrument
    assert resolved.timeframe == planned.timeframe
    assert resolver.registered_ids == (planned.id,)


def test_campaign_example_runs_through_main_cli(
    tmp_path: Path,
) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(tmp_path / "research_cycles.db"),
            "run-market-research-campaign",
            "--design",
            str(_DESIGN_PATH),
            "--registrations",
            str(_REGISTRATION_PATH),
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())

    assert payload["schema_version"] == 1
    assert payload["artifact_type"] == (
        "market_research_campaign"
    )
    assert payload["payload_schema_version"] == 1
    assert payload["producer"] == (
        "market-research-campaign"
    )
    assert payload["correlation_id"] is None
    assert len(payload["source_references"]) == 2

    campaign_payload = payload["payload"]

    assert campaign_payload["experiment_count"] == 1
    assert len(campaign_payload["experiments"]) == 1
