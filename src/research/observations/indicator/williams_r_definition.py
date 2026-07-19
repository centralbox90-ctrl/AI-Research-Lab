from dataclasses import dataclass
from typing import Literal

from src.research.observations.indicator.definition import (
    IndicatorObservationDefinition,
)


WilliamsCrossDirection = Literal[
    "cross_above",
    "cross_below",
]


@dataclass(frozen=True, slots=True)
class WilliamsRObservationDefinition(
    IndicatorObservationDefinition,
):
    """
    Reproducible definition of a Williams %R level crossing.
    """

    level: float
    direction: WilliamsCrossDirection

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.indicator.indicator_type != "williams_r":
            raise ValueError(
                "WilliamsRObservationDefinition requires "
                "indicator_type='williams_r'"
            )

        if not -100.0 <= self.level <= 0.0:
            raise ValueError(
                "level must be between -100 and 0"
            )

        if self.direction not in {
            "cross_above",
            "cross_below",
        }:
            raise ValueError(
                "direction must be 'cross_above' or "
                "'cross_below'"
            )