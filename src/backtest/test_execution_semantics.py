import pandas as pd

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
    ExitReason,
)


def test_short_stop_loss_has_priority_over_take_profit() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                100.0,
            ],
            "High": [
                100.0,
                103.0,
            ],
            "Low": [
                100.0,
                97.0,
            ],
            "AI_prediction": [
                -1,
                -1,
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
    assert trades[0].exit_reason == ExitReason.STOP_LOSS
    assert trades[0].exit_price == 102.0


def test_open_position_closes_at_end_of_data() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                101.0,
            ],
            "High": [
                100.0,
                101.0,
            ],
            "Low": [
                100.0,
                100.0,
            ],
            "AI_prediction": [
                1,
                1,
            ],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=50.0,
        take_profit_percent=50.0,
        max_holding_bars=10,
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
        execution_policy=policy,
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == ExitReason.END_OF_DATA
    assert trades[0].exit_price == 101.0