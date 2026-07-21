import pytest

from src.backtest.execution_types import (
    ExitReason,
    PositionSide,
)
from src.backtest.trade import Trade


@pytest.mark.parametrize(
    ("side", "exit_price", "expected_profit"),
    [
        (
            PositionSide.LONG,
            102.0,
            1.9,
        ),
        (
            PositionSide.SHORT,
            98.0,
            1.9,
        ),
    ],
)
def test_commission_percent_is_total_round_trip_cost(
    side: PositionSide,
    exit_price: float,
    expected_profit: float,
) -> None:
    trade = Trade(
        symbol="BTCUSDT",
        timeframe="1H",
        side=side,
        entry_time=0,
        entry_price=100.0,
        entry_signal=1,
        commission_percent=0.1,
    )

    trade.close(
        exit_time=1,
        exit_price=exit_price,
        reason=ExitReason.DECISION_EXIT,
    )

    assert trade.profit_percent == pytest.approx(
        expected_profit
    )


def test_zero_commission_preserves_gross_profit() -> None:
    trade = Trade(
        symbol="BTCUSDT",
        timeframe="1H",
        side=PositionSide.LONG,
        entry_time=0,
        entry_price=100.0,
        entry_signal=1,
        commission_percent=0.0,
    )

    trade.close(
        exit_time=1,
        exit_price=102.0,
        reason=ExitReason.DECISION_EXIT,
    )

    assert trade.profit_percent == pytest.approx(2.0)
