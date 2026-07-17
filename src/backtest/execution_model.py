from dataclasses import dataclass

from src.backtest.execution_types import PositionSide


@dataclass(frozen=True)
class ExecutionModel:
    """
    Calculates executed prices for simulated orders.

    Slippage is always adverse:
    - LONG entry executes above the requested price;
    - SHORT entry executes below the requested price;
    - LONG exit executes below the requested price;
    - SHORT exit executes above the requested price.
    """

    commission_percent: float
    slippage_percent: float

    def __post_init__(self) -> None:
        if self.commission_percent < 0:
            raise ValueError(
                "commission_percent must not be negative"
            )

        if self.slippage_percent < 0:
            raise ValueError(
                "slippage_percent must not be negative"
            )

    def entry_price(
        self,
        price: float,
        side: PositionSide,
    ) -> float:
        multiplier = self.slippage_percent / 100

        if side == PositionSide.LONG:
            return price * (1 + multiplier)

        if side == PositionSide.SHORT:
            return price * (1 - multiplier)

        raise ValueError(
            f"Unsupported position side: {side!r}"
        )

    def exit_price(
        self,
        price: float,
        side: PositionSide,
    ) -> float:
        multiplier = self.slippage_percent / 100

        if side == PositionSide.LONG:
            return price * (1 - multiplier)

        if side == PositionSide.SHORT:
            return price * (1 + multiplier)

        raise ValueError(
            f"Unsupported position side: {side!r}"
        )
