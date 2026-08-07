from __future__ import annotations

from src.indicators.series import IndicatorSeries
from src.signals.descriptor import (
    SignalRuleDescriptor,
)
from src.signals.signal import (
    MarketSignal,
    MarketSignalDirection,
)


class LongOnObservationRule:
    """Convert any declared observation event to LONG."""

    def generate(
        self,
        series: IndicatorSeries,
        observations: tuple[int, ...],
    ) -> tuple[MarketSignal, ...]:
        if len(series) != len(observations):
            raise ValueError(
                "series and observations length mismatch"
            )

        invalid = tuple(
            value
            for value in observations
            if value not in (-1, 0, 1)
        )

        if invalid:
            raise ValueError(
                "observations must contain only "
                "-1, 0 or 1"
            )

        return tuple(
            MarketSignal(
                MarketSignalDirection.LONG
                if value != 0
                else MarketSignalDirection.NEUTRAL
            )
            for value in observations
        )


SIGNAL_RULE = SignalRuleDescriptor(
    rule_id="long_on_observation",
    version=1,
    rule=LongOnObservationRule(),
)
