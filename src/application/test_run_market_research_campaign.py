from datetime import datetime, timezone

import pytest

from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_campaign_plan_market_adapter import (
    ResearchCampaignPlanMarketAdapter,
    ResolvedMarketExperiment,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignExperimentResult,
    MarketResearchCampaignResult,
    RunMarketResearchCampaign,
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


class RecordingMarketResearchRunner:
    def __init__(self) -> None:
        self.received: list[
            MarketExperimentSpecification
        ] = []
        self.results: list[
            NextExperimentResearchCycleResult
        ] = []

    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        self.received.append(specification)
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
        timeframes=(
            "H1",
            "H4",
        ),
        data_periods=("training-period-v1",),
        indicator_configurations=("rsi-period-14",),
        signal_rules=("rsi-oversold-entry-v1",),
        execution_policies=("long-stop-take-v1",),
        baselines=("unconditional-return-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparative-plan-v1",
        provenance=(
            (
                "question_fingerprint",
                "question-fingerprint",
            ),
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
            "Evaluate an RSI oversold signal on historical data."
        ),
        hypothesis_title=(
            "RSI oversold values precede positive returns"
        ),
        hypothesis_description=(
            "The registered RSI signal should produce "
            "positive historical returns."
        ),
        expected_result=(
            "Positive net profit with a non-zero trade count."
        ),
        experiment_title=(
            f"{planned_specification.instrument} "
            f"{planned_specification.timeframe} RSI backtest"
        ),
        experiment_description=(
            "Execute one resolved campaign experiment."
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
        entry_rule="rsi-oversold-entry-v1",
        exit_rule="stop-take-or-max-holding-v1",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "rsi_period": 14,
            "oversold_level": 30,
        },
        tags=(
            planned_specification.campaign_design_id,
            planned_specification.id,
        ),
    )


def build_registrations(
    plan: ResearchCampaignPlan,
) -> dict[str, MarketExperimentSpecification]:
    return {
        planned_specification.id: (
            build_market_specification(
                planned_specification
            )
        )
        for planned_specification
        in plan.experiment_specifications
    }


def build_use_case(
    *,
    planner: ResearchPlanner,
    plan: ResearchCampaignPlan,
    runner: RecordingMarketResearchRunner,
) -> RunMarketResearchCampaign:
    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            build_registrations(plan)
        )
    )

    return RunMarketResearchCampaign(
        planner=planner,
        adapter=ResearchCampaignPlanMarketAdapter(
            resolver
        ),
        runner=runner,
    )


def test_plans_resolves_and_executes_complete_campaign() -> None:
    design = build_design()
    planner = ResearchPlanner()
    expected_plan = planner.plan(design)
    runner = RecordingMarketResearchRunner()
    use_case = build_use_case(
        planner=planner,
        plan=expected_plan,
        runner=runner,
    )

    result = use_case.execute(design)

    assert isinstance(
        result,
        MarketResearchCampaignResult,
    )
    assert result.research_plan.id == expected_plan.id
    assert result.research_plan.experiment_ids == (
        expected_plan.experiment_ids
    )
    assert len(result.experiment_results) == 4
    assert tuple(runner.received) == (
        result.resolved_plan.market_specifications
    )


def test_preserves_result_relationships_and_order() -> None:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    runner = RecordingMarketResearchRunner()

    result = build_use_case(
        planner=planner,
        plan=plan,
        runner=runner,
    ).execute(design)

    assert tuple(
        experiment_result
        .resolved_experiment
        .planned_specification
        .id
        for experiment_result
        in result.experiment_results
    ) == plan.experiment_ids

    assert all(
        isinstance(
            experiment_result,
            MarketResearchCampaignExperimentResult,
        )
        for experiment_result
        in result.experiment_results
    )

    assert all(
        isinstance(
            experiment_result.resolved_experiment,
            ResolvedMarketExperiment,
        )
        for experiment_result
        in result.experiment_results
    )

    assert len(result.results) == len(
        runner.results
    )
    assert all(
        actual is expected
        for actual, expected in zip(
            result.results,
            runner.results,
            strict=True,
        )
    )


def test_campaign_experiment_result_requires_cycle_result(
) -> None:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    runner = RecordingMarketResearchRunner()
    campaign_result = build_use_case(
        planner=planner,
        plan=plan,
        runner=runner,
    ).execute(design)

    with pytest.raises(
        TypeError,
        match=(
            "result must be a "
            "NextExperimentResearchCycleResult"
        ),
    ):
        MarketResearchCampaignExperimentResult(
            resolved_experiment=(
                campaign_result
                .resolved_plan
                .experiments[0]
            ),
            result=object(),
        )


def test_resolves_entire_plan_before_execution() -> None:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    first = plan.experiment_specifications[0]
    runner = RecordingMarketResearchRunner()

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                first.id: build_market_specification(first),
            }
        )
    )

    use_case = RunMarketResearchCampaign(
        planner=planner,
        adapter=ResearchCampaignPlanMarketAdapter(
            resolver
        ),
        runner=runner,
    )

    with pytest.raises(
        ValueError,
        match=(
            "no market experiment specification "
            "registered for planned experiment"
        ),
    ):
        use_case.execute(design)

    assert runner.received == []


def test_rejects_invalid_design_before_planning() -> None:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    runner = RecordingMarketResearchRunner()
    use_case = build_use_case(
        planner=planner,
        plan=plan,
        runner=runner,
    )

    with pytest.raises(
        TypeError,
        match="design must be a CampaignDesign",
    ):
        use_case.execute(object())

    assert runner.received == []


def test_requires_research_planner() -> None:
    design = build_design()
    plan = ResearchPlanner().plan(design)
    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            build_registrations(plan)
        )
    )

    with pytest.raises(
        TypeError,
        match="planner must be a ResearchPlanner",
    ):
        RunMarketResearchCampaign(
            planner=object(),
            adapter=ResearchCampaignPlanMarketAdapter(
                resolver
            ),
            runner=RecordingMarketResearchRunner(),
        )


def test_requires_campaign_plan_adapter() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "adapter must be a "
            "ResearchCampaignPlanMarketAdapter"
        ),
    ):
        RunMarketResearchCampaign(
            planner=ResearchPlanner(),
            adapter=object(),
            runner=RecordingMarketResearchRunner(),
        )


def test_requires_experiment_runner() -> None:
    design = build_design()
    planner = ResearchPlanner()
    plan = planner.plan(design)
    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            build_registrations(plan)
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "runner must provide a callable execute method"
        ),
    ):
        RunMarketResearchCampaign(
            planner=planner,
            adapter=ResearchCampaignPlanMarketAdapter(
                resolver
            ),
            runner=object(),
        )
