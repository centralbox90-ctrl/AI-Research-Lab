import pandas as pd

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
)


def test_backtest_engine_accepts_execution_policy_argument() -> None:
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=3,
                freq="h",
            ),
            "close": [
                100.0,
                105.0,
                110.0,
            ],
            "high": [
                101.0,
                106.0,
                111.0,
            ],
            "low": [
                99.0,
                104.0,
                109.0,
            ],
            "AI_prediction": [
                1,
                1,
                0,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
        execution_policy=policy,
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.side == "BUY"
    assert trade.entry_price == 100.0


def test_execution_policy_controls_take_profit_exit() -> None:
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=4,
                freq="h",
            ),
            "close": [
                100.0,
                101.0,
                103.0,
                103.0,
            ],
            "high": [
                100.0,
                101.0,
                103.0,
                103.0,
            ],
            "low": [
                100.0,
                100.0,
                102.0,
                103.0,
            ],
            "AI_prediction": [
                1,
                1,
                1,
                0,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=5.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
        execution_policy=policy,
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.exit_reason == "take_profit"
    assert trade.exit_price == 102.0


def test_execution_policy_stop_loss_has_priority_over_take_profit() -> None:
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=2,
                freq="h",
            ),
            "close": [
                100.0,
                100.0,
            ],
            "high": [
                103.0,
                103.0,
            ],
            "low": [
                97.0,
                97.0,
            ],
            "AI_prediction": [
                1,
                0,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
        execution_policy=policy,
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.exit_reason == "stop_loss"


def test_execution_policy_controls_max_holding_exit() -> None:
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=4,
                freq="h",
            ),
            "close": [
                100.0,
                101.0,
                102.0,
                103.0,
            ],
            "high": [
                100.0,
                101.0,
                102.0,
                103.0,
            ],
            "low": [
                100.0,
                99.0,
                100.0,
                102.0,
            ],
            "AI_prediction": [
                1,
                1,
                1,
                1,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=50.0,
        take_profit_percent=50.0,
        max_holding_bars=2,
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
        execution_policy=policy,
    )

    assert len(trades) >= 1

    first_trade = trades[0]

    assert first_trade.exit_reason == "max_holding"
    assert first_trade.exit_price == 102.0
    assert first_trade.bars_held == 2
