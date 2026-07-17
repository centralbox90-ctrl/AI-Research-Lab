from src.backtest.execution_types import (
    DecisionAction,
    PositionSide,
)


def map_legacy_signal_to_action(
    signal: int,
    current_side: PositionSide | None,
) -> DecisionAction:
    """
    Converts the legacy numeric signal into an explicit decision action.

    Legacy semantics:
    - 1 opens or maintains a LONG position;
    - -1 opens or maintains a SHORT position;
    - 0 closes an existing position;
    - 0 means no action when no position exists;
    - an opposite signal closes the current position.
    """

    if current_side is None:
        if signal == 1:
            return DecisionAction.OPEN_LONG

        if signal == -1:
            return DecisionAction.OPEN_SHORT

        return DecisionAction.HOLD

    if current_side == PositionSide.LONG:
        if signal == 1:
            return DecisionAction.HOLD

        return DecisionAction.CLOSE

    if current_side == PositionSide.SHORT:
        if signal == -1:
            return DecisionAction.HOLD

        return DecisionAction.CLOSE

    raise ValueError(
        f"Unsupported position side: {current_side!r}"
    )