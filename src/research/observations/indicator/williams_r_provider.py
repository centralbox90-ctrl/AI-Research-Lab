from __future__ import annotations

from uuid import uuid4

from src.indicators.series import IndicatorSeries
from src.research.observations.indicator.provider import (
    IndicatorObservationProvider,
)
from src.research.observations.indicator.williams_r_definition import (
    WilliamsRObservationDefinition,
)
from src.research.observations.observation import Observation


class WilliamsRObservationProvider(
    IndicatorObservationProvider,
):
    """
    Detects Williams %R level crossings.

    This provider creates observations only. It does not create
    trading signals or assign BUY, SELL, LONG, or SHORT semantics.
    """

    def observe(
        self,
        series: IndicatorSeries,
        definition: WilliamsRObservationDefinition,
    ) -> list[Observation]:
        self._validate_inputs(
            series,
            definition,
        )

        observations: list[Observation] = []

        for index in range(1, len(series.values)):
            previous = series.values[index - 1]
            current = series.values[index]

            if previous is None or current is None:
                continue

            if not self._is_crossing(
                previous=previous,
                current=current,
                definition=definition,
            ):
                continue

            observations.append(
                Observation(
                    id=str(uuid4()),
                    definition_id=definition.id,
                    symbol=self._metadata_string(
                        series,
                        "symbol",
                    ),
                    timeframe=self._metadata_string(
                        series,
                        "timeframe",
                    ),
                    timestamp=series.timestamps[index],
                    bar_index=index,
                    price=None,
                    context={
                        "indicator_type": (
                            series.specification.indicator_type
                        ),
                        "indicator_value": float(current),
                        "previous_indicator_value": float(
                            previous
                        ),
                        "level": float(definition.level),
                        "direction": definition.direction,
                    },
                )
            )

        return observations

    def _validate_inputs(
        self,
        series: IndicatorSeries,
        definition: WilliamsRObservationDefinition,
    ) -> None:
        if series.specification != definition.indicator:
            raise ValueError(
                "series specification does not match "
                "observation definition"
            )

    def _is_crossing(
        self,
        *,
        previous: float,
        current: float,
        definition: WilliamsRObservationDefinition,
    ) -> bool:
        if definition.direction == "cross_above":
            return (
                previous <= definition.level
                and current > definition.level
            )

        return (
            previous >= definition.level
            and current < definition.level
        )

    def _metadata_string(
        self,
        series: IndicatorSeries,
        name: str,
    ) -> str:
        value = series.metadata.get(
            name,
            "unknown",
        )

        return str(value)