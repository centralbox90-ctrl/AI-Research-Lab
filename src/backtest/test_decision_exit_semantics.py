import pandas as pd

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
    ExitReason,
)


def test_zero_signal_closes_long_position() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 101.0],
            "High": [100.0, 101.0],
            "Low": [100.0, 100.0],
            "AI_prediction": [1, 0],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=50.0,
        take_profit_percent=50.0,
        max_holding_bars=10,
    )

    trades = BacktestEngine().run(
        data=data,
        execution_policy=policy,
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == ExitReason.DECISION_EXIT
    assert trades[0].exit_price == 101.0


def test_entry_bar_is_not_counted_as_held_bar() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0],
            "High": [100.0, 101.0, 102.0],
            "Low": [100.0, 100.0, 101.0],
            "AI_prediction": [1, 1, 1],
        }
    )

    policy = ExecutionPolicy(
        stop_loss_percent=50.0,
        take_profit_percent=50.0,
        max_holding_bars=2,
    )

    trades = BacktestEngine().run(
        data=data,
        execution_policy=policy,
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == ExitReason.MAX_HOLDING
    assert trades[0].bars_held == 2
    assert trades[0].exit_price == 102.0