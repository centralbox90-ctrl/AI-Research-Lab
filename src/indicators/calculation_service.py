from __future__ import annotations

import pandas as pd

from src.indicators.catalog import IndicatorCatalog
from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification


class IndicatorCalculationService:
    """Выполняет расчёт индикатора через каталог плагинов."""

    def __init__(
        self,
        catalog: IndicatorCatalog,
    ) -> None:
        self._catalog = catalog

    def calculate(
        self,
        data: pd.DataFrame,
        specification: IndicatorSpecification,
    ) -> IndicatorSeries:
        descriptor = self._catalog.get(
            specification.indicator_type,
        )

        return descriptor.calculator(
            data,
            specification,
        )