from dataclasses import dataclass
from datetime import datetime

from src.backtest.execution_types import ExitReason, PositionSide


@dataclass
class Trade:
    """
    Stores complete information about one executed trade.
    """

    symbol: str
    timeframe: str

    side: PositionSide

    entry_time: datetime
    entry_price: float
    entry_signal: int

    exit_time: datetime | None = None
    exit_price: float | None = None
    exit_reason: ExitReason | None = None

    profit_percent: float = 0.0
    bars_held: int = 0

    max_profit_percent: float = 0.0
    max_drawdown_percent: float = 0.0

    commission_percent: float = 0.0

    def close(
        self,
        exit_time: datetime,
        exit_price: float,
        reason: ExitReason,
    ) -> None:
        """
        Close trade and calculate final result.
        """

        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = reason

        if self.side == PositionSide.LONG:
            gross_profit = (
                (exit_price - self.entry_price)
                / self.entry_price
            ) * 100

        elif self.side == PositionSide.SHORT:
            gross_profit = (
                (self.entry_price - exit_price)
                / self.entry_price
            ) * 100

        else:
            gross_profit = 0.0

        self.profit_percent = (
            gross_profit
            - self.commission_percent
        )

    def as_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "side": self.side,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "profit_percent": self.profit_percent,
            "bars_held": self.bars_held,
            "max_profit_percent": self.max_profit_percent,
            "max_drawdown_percent": self.max_drawdown_percent,
            "entry_signal": self.entry_signal,
            "exit_reason": self.exit_reason,
        }
