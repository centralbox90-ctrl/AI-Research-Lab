from __future__ import annotations

from src.indicators.series import IndicatorSeries
from src.signals.signal import (
    MarketSignal,
    MarketSignalDirection,
)


class IndicatorSignalRule:
    """
    Default indicator observation to market signal rule.
    """

    def generate(
        self,
        series: IndicatorSeries,
        observations: tuple[int, ...],
    ) -> tuple[MarketSignal, ...]:

        if len(series) != len(observations):
            raise ValueError(
                "series and observations length mismatch"
            )

        return tuple(
            MarketSignal(
                MarketSignalDirection(value)
            )
            for value in observations
        )