import pandas as pd

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
)


def test_short_position_take_profit_exit() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                97.0,
                97.0,
            ],
            "High": [
                100.0,
                98.0,
                97.0,
            ],
            "Low": [
                100.0,
                96.0,
                97.0,
            ],
            "AI_prediction": [
                -1,
                -1,
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

    assert trade.side == "SELL"
    assert trade.exit_reason == "take_profit"
    assert trade.exit_price == 98.0
    assert trade.profit_percent == 2.0


def test_short_position_stop_loss_exit() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                103.0,
            ],
            "High": [
                100.0,
                104.0,
            ],
            "Low": [
                100.0,
                102.0,
            ],
            "AI_prediction": [
                -1,
                0,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=2.0,
        take_profit_percent=5.0,
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

    assert trade.side == "SELL"
    assert trade.exit_reason == "stop_loss"
    assert trade.exit_price == 102.0
    assert trade.profit_percent == -2.0


def test_short_position_max_holding_exit() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                99.0,
                98.0,
                97.0,
            ],
            "High": [
                100.0,
                100.0,
                99.0,
                98.0,
            ],
            "Low": [
                100.0,
                98.0,
                97.0,
                96.0,
            ],
            "AI_prediction": [
                -1,
                -1,
                -1,
                -1,
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

    trade = trades[0]

    assert trade.side == "SELL"
    assert trade.exit_reason == "max_holding"
    assert trade.exit_price == 98.0