from datetime import datetime

from src.backtest.execution_policy import ExecutionPolicy
from src.backtest.execution_types import (
    DecisionAction,
    ExitReason,
    PositionSide,
)
from src.backtest.position import Position
from src.backtest.position_exit_evaluator import (
    ExitDecision,
    PositionExitEvaluator,
)


def build_position(
    side: PositionSide,
    *,
    bars_held: int = 1,
) -> Position:
    return Position(
        symbol="BTCUSDT",
        timeframe="1H",
        side=side,
        entry_time=datetime(2026, 1, 1),
        entry_price=100.0,
        entry_signal=1,
        bars_held=bars_held,
    )


def build_policy(
    *,
    max_holding_bars: int = 10,
) -> ExecutionPolicy:
    return ExecutionPolicy(
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=max_holding_bars,
    )


def test_long_stop_loss_has_priority_over_take_profit() -> None:
    decision = PositionExitEvaluator().evaluate(
        position=build_position(PositionSide.LONG),
        close_price=100.0,
        high_price=103.0,
        low_price=97.0,
        action=DecisionAction.HOLD,
        policy=build_policy(),
    )

    assert decision == ExitDecision(
        requested_price=98.0,
        reason=ExitReason.STOP_LOSS,
    )


def test_short_stop_loss_has_priority_over_take_profit() -> None:
    decision = PositionExitEvaluator().evaluate(
        position=build_position(PositionSide.SHORT),
        close_price=100.0,
        high_price=103.0,
        low_price=97.0,
        action=DecisionAction.HOLD,
        policy=build_policy(),
    )

    assert decision == ExitDecision(
        requested_price=102.0,
        reason=ExitReason.STOP_LOSS,
    )


def test_max_holding_exit_uses_close_price() -> None:
    decision = PositionExitEvaluator().evaluate(
        position=build_position(
            PositionSide.LONG,
            bars_held=2,
        ),
        close_price=101.0,
        high_price=101.0,
        low_price=99.0,
        action=DecisionAction.HOLD,
        policy=build_policy(max_holding_bars=2),
    )

    assert decision == ExitDecision(
        requested_price=101.0,
        reason=ExitReason.MAX_HOLDING,
    )


def test_decision_exit_uses_close_price() -> None:
    decision = PositionExitEvaluator().evaluate(
        position=build_position(PositionSide.LONG),
        close_price=101.0,
        high_price=101.0,
        low_price=99.0,
        action=DecisionAction.CLOSE,
        policy=build_policy(),
    )

    assert decision == ExitDecision(
        requested_price=101.0,
        reason=ExitReason.DECISION_EXIT,
    )


def test_hold_without_trigger_returns_none() -> None:
    decision = PositionExitEvaluator().evaluate(
        position=build_position(PositionSide.LONG),
        close_price=101.0,
        high_price=101.0,
        low_price=99.0,
        action=DecisionAction.HOLD,
        policy=build_policy(),
    )

    assert decision is None
