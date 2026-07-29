import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.application.campaign_design_loader import (
    CampaignDesignLoader,
)
from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_registration_loader import (
    MarketExperimentRegistrationLoader,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignResult,
)
from src.cli.market_research_campaign_presenter import (
    MarketResearchCampaignPresenter,
)
from src.cli.run_market_research_campaign_command import (
    RunMarketResearchCampaignCommand,
)
from src.research.campaign_design import CampaignDesign
from src.research.cycle_results import (
    NextExperimentResearchCycleResult,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
    ResearchPlanner,
)


class StubCampaignDesignLoader(
    CampaignDesignLoader
):
    def __init__(
        self,
        design: CampaignDesign,
    ) -> None:
        self.design = design
        self.paths: list[str | Path] = []

    def load(
        self,
        path: str | Path,
    ) -> CampaignDesign:
        self.paths.append(path)

        return self.design


class StubRegistrationLoader(
    MarketExperimentRegistrationLoader
):
    def __init__(
        self,
        resolver: (
            InMemoryMarketExperimentSpecificationResolver
        ),
    ) -> None:
        self.resolver = resolver
        self.calls: list[
            tuple[
                str | Path,
                ResearchCampaignPlan,
            ]
        ] = []

    def load(
        self,
        path: str | Path,
        *,
        plan: ResearchCampaignPlan,
    ) -> InMemoryMarketExperimentSpecificationResolver:
        self.calls.append(
            (
                path,
                plan,
            )
        )

        return self.resolver


class StubCampaignPresenter(
    MarketResearchCampaignPresenter
):
    def __init__(self) -> None:
        self.results: list[
            MarketResearchCampaignResult
        ] = []

    def present(
        self,
        result: MarketResearchCampaignResult,
    ) -> dict[str, object]:
        self.results.append(result)

        return {
            "artifact_type": (
                "market_research_campaign"
            ),
            "campaign_plan_id": (
                result.research_plan.id
            ),
            "experiment_count": len(
                result.experiment_results
            ),
        }


class RecordingRunner:
    def __init__(self) -> None:
        self.specifications: list[
            MarketExperimentSpecification
        ] = []
        self.results: list[
            NextExperimentResearchCycleResult
        ] = []

    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        self.specifications.append(specification)
        result = object.__new__(
            NextExperimentResearchCycleResult
        )
        self.results.append(result)

        return result


def build_design() -> CampaignDesign:
    return CampaignDesign(
        question_id="question-rsi",
        hypothesis_ids=("hypothesis-rsi",),
        instruments=(
            "BTCUSDT",
            "EURUSD",
        ),
        timeframes=("H1",),
        data_periods=("training-period-v1",),
        indicator_configurations=("rsi-period-14",),
        signal_rules=("rsi-entry-v1",),
        execution_policies=("risk-policy-v1",),
        baselines=("unconditional-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparison-v1",
        provenance=(
            ("source", "command-test"),
        ),
    )


def build_market_specification(
    planned_specification: CampaignExperimentSpecification,
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Does RSI oversold predict positive returns?"
        ),
        question_description=(
            "Evaluate an RSI signal on historical data."
        ),
        hypothesis_title=(
            "RSI oversold values precede positive returns"
        ),
        hypothesis_description=(
            "The registered signal should produce "
            "positive returns."
        ),
        expected_result="Positive net profit.",
        experiment_title=(
            f"{planned_specification.instrument} "
            f"{planned_specification.timeframe} backtest"
        ),
        experiment_description=(
            "Execute one campaign experiment."
        ),
        data_source="historical_csv",
        symbol=planned_specification.instrument,
        timeframe=planned_specification.timeframe,
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="rsi-entry-v1",
        exit_rule="risk-exit-v1",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def build_resolver(
    plan: ResearchCampaignPlan,
    *,
    complete: bool = True,
) -> InMemoryMarketExperimentSpecificationResolver:
    planned_specifications = (
        plan.experiment_specifications
        if complete
        else plan.experiment_specifications[:1]
    )

    return InMemoryMarketExperimentSpecificationResolver(
        {
            planned_specification.id: (
                build_market_specification(
                    planned_specification
                )
            )
            for planned_specification
            in planned_specifications
        }
    )


def build_command(
    *,
    complete: bool = True,
) -> tuple[
    RunMarketResearchCampaignCommand,
    CampaignDesign,
    ResearchCampaignPlan,
    RecordingRunner,
    StubCampaignDesignLoader,
    StubRegistrationLoader,
    StubCampaignPresenter,
]:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    runner = RecordingRunner()
    design_loader = StubCampaignDesignLoader(
        design
    )
    registration_loader = StubRegistrationLoader(
        build_resolver(
            plan,
            complete=complete,
        )
    )
    presenter = StubCampaignPresenter()

    command = RunMarketResearchCampaignCommand(
        runner=runner,
        planner=planner,
        design_loader=design_loader,
        registration_loader=registration_loader,
        presenter=presenter,
    )

    return (
        command,
        design,
        plan,
        runner,
        design_loader,
        registration_loader,
        presenter,
    )


def test_loads_runs_and_presents_campaign() -> None:
    (
        command,
        _,
        plan,
        runner,
        design_loader,
        registration_loader,
        presenter,
    ) = build_command()

    rendered = command.execute(
        Path("campaign-design.json"),
        Path("campaign-registrations.json"),
    )
    payload = json.loads(rendered)

    assert design_loader.paths == [
        Path("campaign-design.json"),
    ]
    assert len(registration_loader.calls) == 1
    assert registration_loader.calls[0][0] == (
        Path("campaign-registrations.json")
    )
    assert (
        registration_loader.calls[0][1].id
        == plan.id
    )
    assert len(runner.specifications) == 2
    assert len(presenter.results) == 1
    assert payload == {
        "artifact_type": (
            "market_research_campaign"
        ),
        "campaign_plan_id": plan.id,
        "experiment_count": 2,
    }


def test_supports_compact_json() -> None:
    command, _, _, _, _, _, _ = (
        build_command()
    )

    rendered = command.execute(
        "campaign-design.json",
        "campaign-registrations.json",
        indent=None,
    )

    assert "\n" not in rendered
    assert json.loads(rendered)[
        "experiment_count"
    ] == 2


def test_resolves_complete_plan_before_running() -> None:
    (
        command,
        _,
        _,
        runner,
        _,
        _,
        presenter,
    ) = build_command(
        complete=False
    )

    with pytest.raises(
        ValueError,
        match=(
            "no market experiment specification "
            "registered for planned experiment"
        ),
    ):
        command.execute(
            "campaign-design.json",
            "campaign-registrations.json",
        )

    assert runner.specifications == []
    assert presenter.results == []


def test_requires_runner() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "runner must provide a callable execute method"
        ),
    ):
        RunMarketResearchCampaignCommand(
            runner=object()
        )


def test_rejects_invalid_planner() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "planner must be a ResearchPlanner or None"
        ),
    ):
        RunMarketResearchCampaignCommand(
            runner=RecordingRunner(),
            planner=object(),
        )


def test_rejects_invalid_design_loader() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "design_loader must be a "
            "CampaignDesignLoader or None"
        ),
    ):
        RunMarketResearchCampaignCommand(
            runner=RecordingRunner(),
            design_loader=object(),
        )


def test_rejects_invalid_registration_loader() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "registration_loader must be a "
            "MarketExperimentRegistrationLoader or None"
        ),
    ):
        RunMarketResearchCampaignCommand(
            runner=RecordingRunner(),
            registration_loader=object(),
        )


def test_rejects_invalid_presenter() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "presenter must be a "
            "MarketResearchCampaignPresenter or None"
        ),
    ):
        RunMarketResearchCampaignCommand(
            runner=RecordingRunner(),
            presenter=object(),
        )
