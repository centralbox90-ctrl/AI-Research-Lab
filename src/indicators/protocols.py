from typing import Protocol, TypeVar

from src.indicators.series import IndicatorSeries


MarketDataT = TypeVar("MarketDataT", contravariant=True)


class Indicator(Protocol[MarketDataT]):
    """
    Контракт вычислительного индикатора.

    Индикатор преобразует рыночные данные в воспроизводимый
    IndicatorSeries и ничего не знает об исследовательской семантике.
    """

    @property
    def name(self) -> str:
        ...

    @property
    def version(self) -> int:
        ...

    @property
    def warmup_period(self) -> int:
        ...

    def calculate(
        self,
        market_data: MarketDataT,
    ) -> IndicatorSeries:
        ...