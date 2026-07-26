from datetime import datetime

import pytest

from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_types import PositionSide
from src.backtest.position_factory import PositionFactory


@pytest.mark.parametrize(
    ("side", "expected_entry_price"),
    [
        (PositionSide.LONG, 100.1),
        (PositionSide.SHORT, 99.9),
    ],
)
def test_opens_position_with_executed_entry_price(
    side: PositionSide,
    expected_entry_price: float,
) -> None:
    entry_time = datetime(2026, 1, 1)
    execution_model = ExecutionModel(
        commission_percent=0.2,
        slippage_percent=0.1,
    )

    position = PositionFactory().open_position(
        symbol="BTCUSDT",
        timeframe="1H",
        side=side,
        entry_time=entry_time,
        requested_entry_price=100.0,
        entry_signal=1,
        execution_model=execution_model,
    )

    assert position.symbol == "BTCUSDT"
    assert position.timeframe == "1H"
    assert position.side == side
    assert position.entry_time == entry_time
    assert position.entry_price == pytest.approx(
        expected_entry_price
    )
    assert position.entry_signal == 1
    assert position.bars_held == 0
