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
)
from src.research.campaign_design import CampaignDesign
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
    ResearchPlanner,
)


def build_plan(
    *,
    instrument: str = "BTCUSDT",
) -> ResearchCampaignPlan:
    design = CampaignDesign(
        question_id="question-rsi",
        hypothesis_ids=("hypothesis-rsi",),
        instruments=(instrument,),
        timeframes=("H1",),
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

    return ResearchPlanner().plan(design)


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
            f"{planned_specification.instrument} RSI backtest"
        ),
        experiment_description=(
            "Execute the explicitly registered campaign experiment."
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


def test_resolves_explicitly_registered_specification() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )
    market_specification = build_market_specification(
        planned_specification
    )

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                planned_specification.id: (
                    market_specification
                ),
            }
        )
    )

    assert resolver.resolve(
        planned_specification
    ) is market_specification


def test_integrates_with_campaign_plan_adapter() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )
    market_specification = build_market_specification(
        planned_specification
    )

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                planned_specification.id: (
                    market_specification
                ),
            }
        )
    )

    resolved_plan = ResearchCampaignPlanMarketAdapter(
        resolver
    ).adapt(plan)

    assert resolved_plan.research_plan is plan
    assert resolved_plan.market_specifications == (
        market_specification,
    )
    assert (
        resolved_plan.experiments[0]
        .planned_specification
        is planned_specification
    )


def test_copies_registration_mapping() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )
    market_specification = build_market_specification(
        planned_specification
    )
    registrations = {
        planned_specification.id: market_specification,
    }

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            registrations
        )
    )
    registrations.clear()

    assert resolver.resolve(
        planned_specification
    ) is market_specification


def test_exposes_sorted_registered_ids() -> None:
    first_plan = build_plan(instrument="BTCUSDT")
    second_plan = build_plan(instrument="EURUSD")
    first = first_plan.experiment_specifications[0]
    second = second_plan.experiment_specifications[0]

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                second.id: build_market_specification(second),
                first.id: build_market_specification(first),
            }
        )
    )

    assert resolver.registered_ids == tuple(
        sorted(
            (
                first.id,
                second.id,
            )
        )
    )


def test_rejects_missing_registration() -> None:
    registered_plan = build_plan(
        instrument="BTCUSDT"
    )
    missing_plan = build_plan(
        instrument="EURUSD"
    )
    registered = (
        registered_plan.experiment_specifications[0]
    )
    missing = missing_plan.experiment_specifications[0]

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                registered.id: (
                    build_market_specification(registered)
                ),
            }
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "no market experiment specification "
            "registered for planned experiment"
        ),
    ):
        resolver.resolve(missing)


def test_rejects_invalid_planned_specification() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )

    resolver = (
        InMemoryMarketExperimentSpecificationResolver(
            {
                planned_specification.id: (
                    build_market_specification(
                        planned_specification
                    )
                ),
            }
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "planned_specification must be a "
            "CampaignExperimentSpecification"
        ),
    ):
        resolver.resolve(object())


def test_rejects_non_mapping_registrations() -> None:
    with pytest.raises(
        TypeError,
        match="registrations must be a mapping",
    ):
        InMemoryMarketExperimentSpecificationResolver(
            []
        )


def test_rejects_empty_registrations() -> None:
    with pytest.raises(
        ValueError,
        match="registrations must not be empty",
    ):
        InMemoryMarketExperimentSpecificationResolver(
            {}
        )


def test_rejects_non_string_registration_id() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )

    with pytest.raises(
        TypeError,
        match="registration IDs must be strings",
    ):
        InMemoryMarketExperimentSpecificationResolver(
            {
                1: build_market_specification(
                    planned_specification
                ),
            }
        )


def test_rejects_empty_registration_id() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )

    with pytest.raises(
        ValueError,
        match="registration IDs must not be empty",
    ):
        InMemoryMarketExperimentSpecificationResolver(
            {
                " ": build_market_specification(
                    planned_specification
                ),
            }
        )


def test_rejects_invalid_registered_value() -> None:
    plan = build_plan()
    planned_specification = (
        plan.experiment_specifications[0]
    )

    with pytest.raises(
        TypeError,
        match=(
            "registered values must be "
            "MarketExperimentSpecification instances"
        ),
    ):
        InMemoryMarketExperimentSpecificationResolver(
            {
                planned_specification.id: object(),
            }
        )
