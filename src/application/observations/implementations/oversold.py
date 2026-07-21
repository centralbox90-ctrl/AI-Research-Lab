from __future__ import annotations

from collections.abc import Mapping

from src.application.observation_calculation_service import (
    ObservationDescriptor,
)
from src.indicators.series import IndicatorSeries


def calculate_oversold(
    series: IndicatorSeries,
    parameters: Mapping[str, object],
) -> tuple[int, ...]:

    level = int(
        parameters.get(
            "oversold_level",
            -80,
        )
    )

    return tuple(
        1
        if value is not None
        and value <= level
        else 0
        for value in series.values
    )


OBSERVATION = ObservationDescriptor(
    observation_type="oversold",
    calculator=calculate_oversold,
)