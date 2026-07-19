from abc import abstractmethod

from src.indicators.series import IndicatorSeries
from src.research.observations.indicator.definition import (
    IndicatorObservationDefinition,
)
from src.research.observations.observation import Observation
from src.research.observations.provider import ObservationProvider


class IndicatorObservationProvider(ObservationProvider):
    """
    Контракт провайдера наблюдений, основанных на IndicatorSeries.

    Метод find() сохраняется для совместимости с общим
    ObservationProvider, а фактическая доменная операция
    выражена методом observe().
    """

    def find(
        self,
        definition: IndicatorObservationDefinition,
    ) -> list[Observation]:
        raise TypeError(
            "IndicatorObservationProvider requires an IndicatorSeries; "
            "use observe(series, definition)"
        )

    @abstractmethod
    def observe(
        self,
        series: IndicatorSeries,
        definition: IndicatorObservationDefinition,
    ) -> list[Observation]:
        """
        Находит наблюдения в рассчитанном индикаторном ряду.
        """
        ...