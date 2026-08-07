from __future__ import annotations

from collections.abc import Mapping
from math import isfinite

from src.application.observation_calculation_service import (
    ObservationDescriptor,
)
from src.indicators.series import IndicatorSeries


def calculate_band_reentry(
    series: IndicatorSeries,
    parameters: Mapping[str, object],
) -> tuple[int, ...]:
    """Buy on lower-band recovery and sell on upper-band reversal."""

    lower_level = _read_level(parameters, "lower_level")
    upper_level = _read_level(parameters, "upper_level")

    if lower_level >= upper_level:
        raise ValueError(
            "lower_level must be less than upper_level"
        )

    values = series.values
    signals = [0 for _ in values]

    for index in range(1, len(values)):
        previous = values[index - 1]
        current = values[index]

        if previous is None or current is None:
            continue

        if previous < lower_level <= current:
            signals[index] = 1
        elif previous > upper_level >= current:
            signals[index] = -1

    return tuple(signals)


def _read_level(
    parameters: Mapping[str, object],
    name: str,
) -> float:
    if name not in parameters:
        raise ValueError(f"{name} parameter is required")

    value = parameters[name]
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
    ):
        raise TypeError(f"{name} must be a finite number")

    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{name} must be finite")

    return normalized


OBSERVATION = ObservationDescriptor(
    observation_type="band_reentry",
    calculator=calculate_band_reentry,
)
