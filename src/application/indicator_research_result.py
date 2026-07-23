from __future__ import annotations

from dataclasses import dataclass

from src.indicators.series import IndicatorSeries
from src.research.specification import (
    ResearchSpecification,
)
from src.signals.result import MarketSignalResult


@dataclass(frozen=True, slots=True)
class IndicatorResearchResult:
    """
    Result of executing one indicator research specification.

    Contains calculated indicator data and generated
    market signals.
    """

    research_specification: ResearchSpecification
    series: IndicatorSeries
    observations: tuple[int, ...]
    signal_result: MarketSignalResult

    def __post_init__(self) -> None:
        if not isinstance(
            self.observations,
            tuple,
        ):
            raise TypeError(
                "observations must be a tuple"
            )

        for observation in self.observations:
            if (
                not isinstance(observation, int)
                or isinstance(observation, bool)
                or observation not in (-1, 0, 1)
            ):
                raise ValueError(
                    "observations must contain only "
                    "-1, 0, or 1"
                )

        if len(self.series) != len(
            self.observations
        ):
            raise ValueError(
                "series and observations must have "
                "equal length"
            )

        if len(self.observations) != len(
            self.signal_result.signals
        ):
            raise ValueError(
                "observations and signals must have "
                "equal length"
            )