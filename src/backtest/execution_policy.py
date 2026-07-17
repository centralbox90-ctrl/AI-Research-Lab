from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPolicy:
    """
    Deterministic execution rules for market backtesting.

    Defines risk management and trading cost assumptions.
    """

    stop_loss_percent: float
    take_profit_percent: float
    max_holding_bars: int

    commission_percent: float = 0.0
    slippage_percent: float = 0.0

    def __post_init__(self) -> None:
        if self.stop_loss_percent <= 0:
            raise ValueError(
                "stop_loss_percent must be greater than zero"
            )

        if self.take_profit_percent <= 0:
            raise ValueError(
                "take_profit_percent must be greater than zero"
            )

        if (
            not isinstance(self.max_holding_bars, int)
            or isinstance(self.max_holding_bars, bool)
            or self.max_holding_bars <= 0
        ):
            raise ValueError(
                "max_holding_bars must be a positive integer"
            )

        if self.commission_percent < 0:
            raise ValueError(
                "commission_percent must not be negative"
            )

        if self.slippage_percent < 0:
            raise ValueError(
                "slippage_percent must not be negative"
            )