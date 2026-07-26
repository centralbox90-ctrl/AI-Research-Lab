from datetime import datetime

import pytest

from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_types import (
    ExitReason,
    PositionSide,
)
from src.backtest.position import Position
from src.backtest.trade_factory import TradeFactory


def test_creates_closed_trade_from_position() -> None:
    position = Position(
        symbol="BTCUSDT",
        timeframe="1H",
        side=PositionSide.LONG,
        entry_time=datetime(2026, 1, 1),
        entry_price=100.0,
        entry_signal=1,
        bars_held=3,
        max_profit_percent=3.0,
        max_drawdown_percent=-1.0,
    )
    execution_model = ExecutionModel(
        commission_percent=0.2,
        slippage_percent=0.1,
    )

    trade = TradeFactory().create_closed_trade(
        position=position,
        exit_time=datetime(2026, 1, 2),
        requested_exit_price=102.0,
        reason=ExitReason.TAKE_PROFIT,
        execution_model=execution_model,
    )

    assert trade.symbol == position.symbol
    assert trade.timeframe == position.timeframe
    assert trade.side == position.side
    assert trade.entry_time == position.entry_time
    assert trade.entry_price == position.entry_price
    assert trade.entry_signal == position.entry_signal
    assert trade.bars_held == position.bars_held
    assert trade.max_profit_percent == position.max_profit_percent
    assert trade.max_drawdown_percent == position.max_drawdown_percent
    assert trade.exit_time == datetime(2026, 1, 2)
    assert trade.exit_price == pytest.approx(101.898)
    assert trade.exit_reason == ExitReason.TAKE_PROFIT
    assert trade.commission_percent == 0.2
    assert trade.profit_percent == pytest.approx(1.698)
