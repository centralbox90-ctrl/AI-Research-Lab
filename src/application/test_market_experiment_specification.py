from datetime import datetime, timezone

import pytest

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)


def build_specification(
    **overrides: object,
) -> MarketExperimentSpecification:
    values: dict[str, object] = {
        "executor_type": "market_backtest",
        "question_title": (
            "Does the Williams oversold condition predict a rebound?"
        ),
        "question_description": (
            "Test whether an oversold Williams condition is followed "
            "by positive returns."
        ),
        "hypothesis_title": (
            "Williams oversold values precede positive returns"
        ),
        "hypothesis_description": (
            "BTCUSDT is expected to produce positive trade results "
            "after the registered oversold entry rule."
        ),
        "expected_result": (
            "The experiment produces positive net profit with "
            "a non-zero number of trades."
        ),
        "experiment_title": "Williams BTCUSDT historical backtest",
        "experiment_description": (
            "Run the registered Williams entry and exit rules on "
            "historical BTCUSDT data."
        ),
        "data_source": "historical_csv",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_at": datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        "end_at": datetime(
            2024,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        "entry_rule": "williams_oversold_entry",
        "exit_rule": "stop_take_or_max_holding_exit",
        "direction": MarketPositionDirection.LONG,
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 24,
        "commission_percent": 0.1,
        "slippage_percent": 0.05,
        "strategy_parameters": {
            "williams_period": 14,
            "oversold_level": -80,
        },
        "tags": (
            "btc",
            "williams",
            "historical-backtest",
        ),
    }

    values.update(overrides)

    return MarketExperimentSpecification(**values)


def test_market_experiment_specification_accepts_valid_contract() -> None:
    specification = build_specification()

    assert specification.executor_type == "market_backtest"
    assert specification.symbol == "BTCUSDT"
    assert specification.timeframe == "1h"
    assert specification.direction is MarketPositionDirection.LONG
    assert specification.stop_loss_percent == 1.0
    assert specification.take_profit_percent == 2.0
    assert specification.max_holding_bars == 24
    assert specification.strategy_parameters == {
        "williams_period": 14,
        "oversold_level": -80,
    }


def test_market_experiment_specification_rejects_unknown_executor() -> None:
    with pytest.raises(
        ValueError,
        match="executor_type must be 'market_backtest'",
    ):
        build_specification(executor_type="arbitrary_python")


def test_market_experiment_specification_rejects_empty_required_text() -> None:
    with pytest.raises(
        ValueError,
        match="entry_rule must be a non-empty string",
    ):
        build_specification(entry_rule="   ")


def test_market_experiment_specification_rejects_invalid_time_range() -> None:
    timestamp = datetime(
        2024,
        1,
        1,
        tzinfo=timezone.utc,
    )

    with pytest.raises(
        ValueError,
        match="start_at must be earlier than end_at",
    ):
        build_specification(
            start_at=timestamp,
            end_at=timestamp,
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        (
            "stop_loss_percent",
            0.0,
            "stop_loss_percent must be greater than zero",
        ),
        (
            "take_profit_percent",
            -1.0,
            "take_profit_percent must be greater than zero",
        ),
        (
            "max_holding_bars",
            0,
            "max_holding_bars must be a positive integer",
        ),
    ],
)
def test_market_experiment_specification_rejects_invalid_risk_parameters(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        build_specification(
            **{field_name: invalid_value},
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "commission_percent",
        "slippage_percent",
    ],
)
def test_market_experiment_specification_rejects_negative_costs(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be negative",
    ):
        build_specification(
            **{field_name: -0.01},
        )


def test_market_experiment_specification_rejects_mixed_timezone_styles() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "start_at and end_at must use the same timezone style"
        ),
    ):
        build_specification(
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
            ),
        )


def test_market_experiment_specification_rejects_empty_tag() -> None:
    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty strings",
    ):
        build_specification(
            tags=("btc", ""),
        )