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
from src.backtest.position_exit_evaluator import (
    PositionExitEvaluator,
)
from src.backtest.trade import Trade


class BacktestEngine:
    """
    Executes deterministic historical backtests.

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
    ) -> None:
        self.trades: list[Trade] = []
        self._exit_evaluator = (
            exit_evaluator
            or PositionExitEvaluator()
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
                        self._create_trade(
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

                if action == DecisionAction.OPEN_LONG:
                    entry_price = execution_model.entry_price(
                        price=close_price,
                        side=PositionSide.LONG,
                    )

                    position = Position(
                        symbol=symbol,
                        timeframe=timeframe,
                        side=PositionSide.LONG,
                        entry_time=timestamp,
                        entry_price=entry_price,
                        entry_signal=signal,
                    )

                elif action == DecisionAction.OPEN_SHORT:
                    entry_price = execution_model.entry_price(
                        price=close_price,
                        side=PositionSide.SHORT,
                    )

                    position = Position(
                        symbol=symbol,
                        timeframe=timeframe,
                        side=PositionSide.SHORT,
                        entry_time=timestamp,
                        entry_price=entry_price,
                        entry_signal=signal,
                    )

        if position is not None:

            self.trades.append(
                self._create_trade(
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

    def _create_trade(
        self,
        position: Position,
        exit_time,
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
