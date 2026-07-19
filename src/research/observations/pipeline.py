from __future__ import annotations

import pandas as pd

from src.indicators.protocols import Indicator
from src.research.observations.indicator.definition import (
    IndicatorObservationDefinition,
)
from src.research.observations.indicator.provider import (
    IndicatorObservationProvider,
)
from src.research.observations.observation import Observation


class ObservationPipeline:
    """
    Coordinates indicator calculation and observation detection.

    The pipeline intentionally contains no indicator-specific logic.
    """

    def __init__(
        self,
        indicator: Indicator,
        provider: IndicatorObservationProvider,
    ) -> None:
        self._indicator = indicator
        self._provider = provider

    def observe(
        self,
        market_data: pd.DataFrame,
        definition: IndicatorObservationDefinition,
    ) -> list[Observation]:
        series = self._indicator.calculate(
            market_data,
        )

        return self._provider.observe(
            series,
            definition,
        )