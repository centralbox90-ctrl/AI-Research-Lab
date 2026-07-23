from __future__ import annotations

from collections.abc import Mapping
from math import isfinite

from src.application.observation_calculation_service import (
    ObservationDescriptor,
)
from src.indicators.series import IndicatorSeries


_SUPPORTED_DIRECTIONS = frozenset((
    "cross_above",
    "cross_below",
))


def calculate_level_cross(
    series: IndicatorSeries,
    parameters: Mapping[str, object],
) -> tuple[int, ...]:
    level = _read_level(parameters)
    direction = _read_direction(parameters)
    values = series.values
    signals = [0 for _ in values]

    for index in range(1, len(values)):
        previous = values[index - 1]
        current = values[index]

        if previous is None or current is None:
            continue

        if (
            direction == "cross_above"
            and previous < level <= current
        ):
            signals[index] = 1
        elif (
            direction == "cross_below"
            and previous > level >= current
        ):
            signals[index] = -1

    return tuple(signals)


def _read_level(
    parameters: Mapping[str, object],
) -> float:
    if "level" not in parameters:
        raise ValueError("level parameter is required")

    level = parameters["level"]

    if (
        isinstance(level, bool)
        or not isinstance(level, (int, float))
    ):
        raise TypeError("level must be a finite number")

    normalized_level = float(level)

    if not isfinite(normalized_level):
        raise ValueError("level must be finite")

    return normalized_level


def _read_direction(
    parameters: Mapping[str, object],
) -> str:
    if "direction" not in parameters:
        raise ValueError("direction parameter is required")

    direction = parameters["direction"]

    if not isinstance(direction, str):
        raise TypeError("direction must be a string")

    if direction not in _SUPPORTED_DIRECTIONS:
        raise ValueError(
            "direction must be cross_above or cross_below"
        )

    return direction


OBSERVATION = ObservationDescriptor(
    observation_type="level_cross",
    calculator=calculate_level_cross,
)
