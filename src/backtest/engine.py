from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_policy import ExecutionPolicy
from src.backtest.execution_types import (
    DecisionAction,
    ExitReason,
    PositionSide,
)
from src.backtest.legacy_signal_mapper import (
    map_legacy_signal_to_action,
)
from src.backtest.position import Position
from src.backtest.position_factory import PositionFactory
from src.backtest.position_exit_evaluator import (
    PositionExitEvaluator,
)
from src.backtest.trade import Trade
from src.backtest.trade_factory import TradeFactory


class BacktestEngine:
    """
    Orchestrates deterministic historical backtests.

    Supports:
    - LONG positions;
    - SHORT positions;
    - stop loss;
    - take profit;
    - maximum holding period;
    - explicit decision exits.
    """

    def __init__(
        self,
        exit_evaluator: PositionExitEvaluator | None = None,
        position_factory: PositionFactory | None = None,
        trade_factory: TradeFactory | None = None,
    ) -> None:
        self.trades: list[Trade] = []
        self._exit_evaluator = (
            exit_evaluator
            or PositionExitEvaluator()
        )
        self._position_factory = (
            position_factory
            or PositionFactory()
        )
        self._trade_factory = (
            trade_factory
            or TradeFactory()
        )

    def run(
        self,
        data,
        symbol: str = "UNKNOWN",
        timeframe: str = "UNKNOWN",
        execution_policy: ExecutionPolicy | None = None,
    ) -> list[Trade]:

        self.trades = []

        policy = execution_policy or ExecutionPolicy(
            stop_loss_percent=999999,
            take_profit_percent=999999,
            max_holding_bars=999999,
        )

        execution_model = ExecutionModel(
            commission_percent=policy.commission_percent,
            slippage_percent=policy.slippage_percent,
        )

        position: Position | None = None

        for _, row in data.iterrows():

            timestamp = row["timestamp"]
            signal = int(row["AI_prediction"])

            action = map_legacy_signal_to_action(
                signal=signal,
                current_side=(
                    position.side
                    if position is not None
                    else None
                ),
            )

            close_price = float(row["close"])
            high_price = float(row["high"])
            low_price = float(row["low"])

            if position is not None:

                position.update(
                    high=high_price,
                    low=low_price,
                )

                exit_decision = self._exit_evaluator.evaluate(
                    position=position,
                    close_price=close_price,
                    high_price=high_price,
                    low_price=low_price,
                    action=action,
                    policy=policy,
                )

                if exit_decision is not None:
                    self.trades.append(
                        self._trade_factory.create_closed_trade(
                            position=position,
                            exit_time=timestamp,
                            requested_exit_price=(
                                exit_decision.requested_price
                            ),
                            reason=exit_decision.reason,
                            execution_model=execution_model,
                        )
                    )
                    position = None
                    continue

            if position is None:

                if action in (
                    DecisionAction.OPEN_LONG,
                    DecisionAction.OPEN_SHORT,
                ):
                    side = (
                        PositionSide.LONG
                        if action == DecisionAction.OPEN_LONG
                        else PositionSide.SHORT
                    )

                    position = (
                        self._position_factory.open_position(
                            symbol=symbol,
                            timeframe=timeframe,
                            side=side,
                            entry_time=timestamp,
                            requested_entry_price=close_price,
                            entry_signal=signal,
                            execution_model=execution_model,
                        )
                    )

        if position is not None:

            self.trades.append(
                self._trade_factory.create_closed_trade(
                    position=position,
                    exit_time=data.iloc[-1]["timestamp"],
                    requested_exit_price=float(
                        data.iloc[-1]["close"]
                    ),
                    reason=ExitReason.END_OF_DATA,
                    execution_model=execution_model,
                )
            )

        return self.trades
