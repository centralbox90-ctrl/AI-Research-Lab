from datetime import datetime

from src.application.market_assumption_set_builder import (
    build_assumption_set_from_market_specification,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research import AssumptionType


def create_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Question",
        question_description="Question description",
        hypothesis_title="Hypothesis",
        hypothesis_description="Hypothesis description",
        expected_result="Expected result",
        experiment_title="Experiment",
        experiment_description="Experiment description",
        data_source="MT5",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(2024, 1, 1),
        end_at=datetime(2024, 2, 1),
        entry_rule="current_bar_close",
        exit_rule="policy_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        max_holding_bars=10,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "indicator": "williams",
            "period": 14,
        },
    )


def test_builds_execution_and_cost_assumptions() -> None:
    assumption_set = (
        build_assumption_set_from_market_specification(
            create_specification()
        )
    )

    assert assumption_set.get(
        "execution.stop_loss_percent"
    ).value == 2.0

    assert assumption_set.get(
        "cost.commission_percent"
    ).value == 0.1

    assert assumption_set.get(
        "cost.slippage_percent"
    ).value == 0.05


def test_captures_implicit_execution_contracts() -> None:
    assumption_set = (
        build_assumption_set_from_market_specification(
            create_specification()
        )
    )

    assert assumption_set.get(
        "execution.intrabar_conflict_policy"
    ).value == "STOP_LOSS_FIRST"

    assert assumption_set.get(
        "execution.entry_bar_counting"
    ).value == "EXCLUDE_ENTRY_BAR"


def test_builds_scope_and_data_assumptions() -> None:
    assumption_set = (
        build_assumption_set_from_market_specification(
            create_specification()
        )
    )

    symbol = assumption_set.get("scope.symbol")
    data_source = assumption_set.get("data.source")

    assert symbol.value == "EURUSD"
    assert symbol.type == AssumptionType.SCOPE
    assert data_source.type == AssumptionType.DATA
