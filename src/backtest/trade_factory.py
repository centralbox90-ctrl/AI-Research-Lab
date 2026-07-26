from datetime import datetime

from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_types import ExitReason
from src.backtest.position import Position
from src.backtest.trade import Trade


class TradeFactory:
    """Creates completed trade records from closed positions."""

    def create_closed_trade(
        self,
        *,
        position: Position,
        exit_time: datetime,
        requested_exit_price: float,
        reason: ExitReason,
        execution_model: ExecutionModel,
    ) -> Trade:
        executed_exit_price = execution_model.exit_price(
            price=requested_exit_price,
            side=position.side,
        )

        trade = Trade(
            symbol=position.symbol,
            timeframe=position.timeframe,
            side=position.side,
            entry_time=position.entry_time,
            entry_price=position.entry_price,
            entry_signal=position.entry_signal,
            bars_held=position.bars_held,
            max_profit_percent=position.max_profit_percent,
            max_drawdown_percent=position.max_drawdown_percent,
            commission_percent=(
                execution_model.commission_percent
            ),
        )

        trade.close(
            exit_time=exit_time,
            exit_price=executed_exit_price,
            reason=reason,
        )

        return trade
