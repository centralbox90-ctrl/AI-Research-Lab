from datetime import datetime, timezone

import pytest

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_campaign_plan_market_adapter import (
    MarketExperimentSpecificationResolver,
    ResearchCampaignPlanMarketAdapter,
    ResolvedMarketCampaignPlan,
    ResolvedMarketExperiment,
)
from src.research.campaign_design import CampaignDesign
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
    ResearchPlanner,
)


class StubMarketSpecificationResolver:
    def __init__(
        self,
        *,
        symbol_override: str | None = None,
        timeframe_override: str | None = None,
    ) -> None:
        self.symbol_override = symbol_override
        self.timeframe_override = timeframe_override
        self.resolved: list[
            CampaignExperimentSpecification
        ] = []

    def resolve(
        self,
        planned_specification: CampaignExperimentSpecification,
    ) -> MarketExperimentSpecification:
        self.resolved.append(planned_specification)

        return MarketExperimentSpecification(
            executor_type="market_backtest",
            question_title="Does the signal predict returns?",
            question_description=(
                "Evaluate a registered signal on historical data."
            ),
            hypothesis_title=(
                f"Hypothesis {planned_specification.hypothesis_id}"
            ),
            hypothesis_description=(
                "The registered signal should produce positive returns."
            ),
            expected_result="Positive risk-adjusted returns.",
            experiment_title=(
                f"{planned_specification.instrument} "
                f"{planned_specification.timeframe} experiment"
            ),
            experiment_description=(
                "Execute the planned market experiment."
            ),
            data_source="historical_csv",
            symbol=(
                self.symbol_override
                or planned_specification.instrument
            ),
            timeframe=(
                self.timeframe_override
                or planned_specification.timeframe
            ),
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
            entry_rule=planned_specification.signal_rule,
            exit_rule="registered-exit-rule-v1",
            direction=MarketPositionDirection.LONG,
            stop_loss_percent=1.0,
            take_profit_percent=2.0,
            max_holding_bars=24,
            strategy_parameters={
                "indicator_configuration": (
                    planned_specification
                    .indicator_configuration
                ),
                "execution_policy": (
                    planned_specification.execution_policy
                ),
                "baseline": planned_specification.baseline,
                "validation_strategy": (
                    planned_specification.validation_strategy
                ),
                "evaluation_plan_ref": (
                    planned_specification.evaluation_plan_ref
                ),
            },
            tags=(
                planned_specification.campaign_design_id,
                planned_specification.id,
            ),
        )


class InvalidMarketSpecificationResolver:
    def resolve(
        self,
        planned_specification: CampaignExperimentSpecification,
    ) -> object:
        return object()


def build_plan() -> ResearchCampaignPlan:
    design = CampaignDesign(
        question_id="question-signal",
        hypothesis_ids=("hypothesis-signal",),
        instruments=(
            "BTCUSDT",
            "EURUSD",
        ),
        timeframes=("H1",),
        data_periods=("training-period-v1",),
        indicator_configurations=("rsi-period-14",),
        signal_rules=("rsi-oversold-entry-v1",),
        execution_policies=("long-stop-take-v1",),
        baselines=("unconditional-return-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparative-plan-v1",
        provenance=(
            ("question_fingerprint", "question-fingerprint"),
        ),
    )

    return ResearchPlanner().plan(design)


def test_adapter_resolves_complete_campaign_plan() -> None:
    plan = build_plan()
    resolver = StubMarketSpecificationResolver()

    resolved = ResearchCampaignPlanMarketAdapter(
        resolver
    ).adapt(plan)

    assert isinstance(
        resolved,
        ResolvedMarketCampaignPlan,
    )
    assert resolved.research_plan is plan
    assert len(resolved.experiments) == 2
    assert len(resolved.market_specifications) == 2

    assert tuple(resolver.resolved) == (
        plan.experiment_specifications
    )


def test_adapter_preserves_each_planned_specification() -> None:
    plan = build_plan()

    resolved = ResearchCampaignPlanMarketAdapter(
        StubMarketSpecificationResolver()
    ).adapt(plan)

    for source, experiment in zip(
        plan.experiment_specifications,
        resolved.experiments,
        strict=True,
    ):
        assert isinstance(
            experiment,
            ResolvedMarketExperiment,
        )
        assert experiment.planned_specification is source
        assert (
            experiment.market_specification.symbol
            == source.instrument
        )
        assert (
            experiment.market_specification.timeframe
            == source.timeframe
        )


def test_adapter_preserves_plan_order() -> None:
    plan = build_plan()

    resolved = ResearchCampaignPlanMarketAdapter(
        StubMarketSpecificationResolver()
    ).adapt(plan)

    assert tuple(
        experiment.planned_specification.id
        for experiment in resolved.experiments
    ) == plan.experiment_ids


def test_adapter_rejects_invalid_plan() -> None:
    with pytest.raises(
        TypeError,
        match="plan must be a ResearchCampaignPlan",
    ):
        ResearchCampaignPlanMarketAdapter(
            StubMarketSpecificationResolver()
        ).adapt(object())


def test_adapter_requires_resolver_method() -> None:
    with pytest.raises(
        TypeError,
        match="resolver must provide a callable resolve method",
    ):
        ResearchCampaignPlanMarketAdapter(object())


def test_adapter_rejects_invalid_resolver_result() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "market_specification must be a "
            "MarketExperimentSpecification"
        ),
    ):
        ResearchCampaignPlanMarketAdapter(
            InvalidMarketSpecificationResolver()
        ).adapt(build_plan())


def test_adapter_rejects_mismatched_symbol() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "symbol must match the planned instrument"
        ),
    ):
        ResearchCampaignPlanMarketAdapter(
            StubMarketSpecificationResolver(
                symbol_override="XAUUSD",
            )
        ).adapt(build_plan())


def test_adapter_rejects_mismatched_timeframe() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "timeframe must match the planned timeframe"
        ),
    ):
        ResearchCampaignPlanMarketAdapter(
            StubMarketSpecificationResolver(
                timeframe_override="D1",
            )
        ).adapt(build_plan())


def test_resolver_satisfies_protocol_shape() -> None:
    resolver: MarketExperimentSpecificationResolver = (
        StubMarketSpecificationResolver()
    )

    specification = build_plan().experiment_specifications[0]

    assert isinstance(
        resolver.resolve(specification),
        MarketExperimentSpecification,
    )
