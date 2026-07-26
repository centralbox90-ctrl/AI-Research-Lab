from datetime import datetime

from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_types import PositionSide
from src.backtest.position import Position


class PositionFactory:
    """Creates open positions using the execution model."""

    def open_position(
        self,
        *,
        symbol: str,
        timeframe: str,
        side: PositionSide,
        entry_time: datetime,
        requested_entry_price: float,
        entry_signal: int,
        execution_model: ExecutionModel,
    ) -> Position:
        entry_price = execution_model.entry_price(
            price=requested_entry_price,
            side=side,
        )

        return Position(
            symbol=symbol,
            timeframe=timeframe,
            side=side,
            entry_time=entry_time,
            entry_price=entry_price,
            entry_signal=entry_signal,
        )
