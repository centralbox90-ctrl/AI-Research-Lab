from __future__ import annotations

import pandas as pd

from src.application.indicator_market_signal_provider import (
    IndicatorMarketSignalProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)


class HybridMarketSignalProvider(
    MarketSignalProvider,
):
    """
    Selects signal generation implementation.

    If research_specification exists:
        use indicator pipeline.

    Otherwise:
        use simple development signal provider.
    """

    def __init__(
        self,
        *,
        indicator_provider: IndicatorMarketSignalProvider,
        simple_provider: SimpleMarketSignalProvider,
    ) -> None:
        self._indicator_provider = indicator_provider
        self._simple_provider = simple_provider

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:

        if specification.research_specification is None:
            return self._simple_provider.generate(
                data,
                specification,
            )

        return self._indicator_provider.generate(
            data,
            specification,
        )