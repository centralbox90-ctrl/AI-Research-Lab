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
    signal_result: MarketSignalResult

    def __post_init__(self) -> None:
        if len(self.series) != len(
            self.signal_result.signals
        ):
            raise ValueError(
                "series and signals must have equal length"
            )