from dataclasses import dataclass
from datetime import datetime

from src.backtest.execution_types import PositionSide
@dataclass
class Position:
    """
    Текущая открытая позиция.
    Используется Backtest Engine.
    """

    symbol: str
    timeframe: str

    side: PositionSide

    entry_time: datetime
    entry_price: float

    entry_signal: int

    bars_held: int = 0

    highest_price: float = 0.0
    lowest_price: float = 0.0

    max_profit_percent: float = 0.0
    max_drawdown_percent: float = 0.0

    def update(self, high: float, low: float) -> None:
        """
        Обновляет статистику позиции на каждом новом баре.
        """

        self.bars_held += 1

        if self.highest_price == 0:
            self.highest_price = self.entry_price

        if self.lowest_price == 0:
            self.lowest_price = self.entry_price

        self.highest_price = max(self.highest_price, high)
        self.lowest_price = min(self.lowest_price, low)

        if self.side == PositionSide.LONG:

            profit = (
                (self.highest_price - self.entry_price)
                / self.entry_price
            ) * 100

            drawdown = (
                (self.lowest_price - self.entry_price)
                / self.entry_price
            ) * 100

        else:

            profit = (
                (self.entry_price - self.lowest_price)
                / self.entry_price
            ) * 100

            drawdown = (
                (self.entry_price - self.highest_price)
                / self.entry_price
            ) * 100

        self.max_profit_percent = max(
            self.max_profit_percent,
            profit
        )

        self.max_drawdown_percent = min(
            self.max_drawdown_percent,
            drawdown
        )