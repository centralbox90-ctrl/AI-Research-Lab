import pytest

from src.backtest.execution_model import ExecutionModel
from src.backtest.execution_types import PositionSide


@pytest.mark.parametrize(
    ("side", "expected"),
    [
        (PositionSide.LONG, 100.1),
        (PositionSide.SHORT, 99.9),
    ],
)
def test_entry_price_applies_adverse_slippage(
    side: PositionSide,
    expected: float,
) -> None:
    model = ExecutionModel(
        commission_percent=0.0,
        slippage_percent=0.1,
    )

    assert model.entry_price(
        price=100.0,
        side=side,
    ) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("side", "expected"),
    [
        (PositionSide.LONG, 99.9),
        (PositionSide.SHORT, 100.1),
    ],
)
def test_exit_price_applies_adverse_slippage(
    side: PositionSide,
    expected: float,
) -> None:
    model = ExecutionModel(
        commission_percent=0.0,
        slippage_percent=0.1,
    )

    assert model.exit_price(
        price=100.0,
        side=side,
    ) == pytest.approx(expected)


def test_zero_slippage_preserves_price() -> None:
    model = ExecutionModel(
        commission_percent=0.0,
        slippage_percent=0.0,
    )

    assert model.entry_price(
        price=100.0,
        side=PositionSide.LONG,
    ) == 100.0

    assert model.exit_price(
        price=100.0,
        side=PositionSide.LONG,
    ) == 100.0
