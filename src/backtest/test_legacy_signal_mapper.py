import pytest

from src.backtest.execution_types import (
    DecisionAction,
    PositionSide,
)
from src.backtest.legacy_signal_mapper import (
    map_legacy_signal_to_action,
)


@pytest.mark.parametrize(
    ("signal", "current_side", "expected"),
    [
        (
            1,
            None,
            DecisionAction.OPEN_LONG,
        ),
        (
            -1,
            None,
            DecisionAction.OPEN_SHORT,
        ),
        (
            0,
            None,
            DecisionAction.HOLD,
        ),
        (
            1,
            PositionSide.LONG,
            DecisionAction.HOLD,
        ),
        (
            0,
            PositionSide.LONG,
            DecisionAction.CLOSE,
        ),
        (
            -1,
            PositionSide.LONG,
            DecisionAction.CLOSE,
        ),
        (
            -1,
            PositionSide.SHORT,
            DecisionAction.HOLD,
        ),
        (
            0,
            PositionSide.SHORT,
            DecisionAction.CLOSE,
        ),
        (
            1,
            PositionSide.SHORT,
            DecisionAction.CLOSE,
        ),
    ],
)
def test_maps_legacy_signal_to_explicit_action(
    signal: int,
    current_side: PositionSide | None,
    expected: DecisionAction,
) -> None:
    assert (
        map_legacy_signal_to_action(
            signal=signal,
            current_side=current_side,
        )
        == expected
    )
