from dataclasses import dataclass

from src.backtest.execution_policy import ExecutionPolicy
from src.backtest.execution_types import (
    DecisionAction,
    ExitReason,
    PositionSide,
)
from src.backtest.position import Position


@dataclass(frozen=True)
class ExitDecision:
    """Describes a requested deterministic position exit."""

    requested_price: float
    reason: ExitReason


class PositionExitEvaluator:
    """Evaluates deterministic exit rules for one open position."""

    def evaluate(
        self,
        *,
        position: Position,
        close_price: float,
        high_price: float,
        low_price: float,
        action: DecisionAction,
        policy: ExecutionPolicy,
    ) -> ExitDecision | None:
        if position.side == PositionSide.LONG:
            stop_price = (
                position.entry_price
                * (1 - policy.stop_loss_percent / 100)
            )
            take_price = (
                position.entry_price
                * (1 + policy.take_profit_percent / 100)
            )

            if low_price <= stop_price:
                return ExitDecision(
                    requested_price=stop_price,
                    reason=ExitReason.STOP_LOSS,
                )

            if high_price >= take_price:
                return ExitDecision(
                    requested_price=take_price,
                    reason=ExitReason.TAKE_PROFIT,
                )

        elif position.side == PositionSide.SHORT:
            stop_price = (
                position.entry_price
                * (1 + policy.stop_loss_percent / 100)
            )
            take_price = (
                position.entry_price
                * (1 - policy.take_profit_percent / 100)
            )

            if high_price >= stop_price:
                return ExitDecision(
                    requested_price=stop_price,
                    reason=ExitReason.STOP_LOSS,
                )

            if low_price <= take_price:
                return ExitDecision(
                    requested_price=take_price,
                    reason=ExitReason.TAKE_PROFIT,
                )

        if position.bars_held >= policy.max_holding_bars:
            return ExitDecision(
                requested_price=close_price,
                reason=ExitReason.MAX_HOLDING,
            )

        if action == DecisionAction.CLOSE:
            return ExitDecision(
                requested_price=close_price,
                reason=ExitReason.DECISION_EXIT,
            )

        return None
