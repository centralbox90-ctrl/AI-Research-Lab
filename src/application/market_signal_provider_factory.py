from __future__ import annotations

from src.application.hybrid_market_signal_provider import (
    HybridMarketSignalProvider,
)
from src.application.indicator_market_signal_provider import (
    IndicatorMarketSignalProvider,
)
from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)


class MarketSignalProviderFactory:
    """
    Creates configured market signal provider.
    """

    def __init__(
        self,
        *,
        indicator_research_execution_service: (
            IndicatorResearchExecutionService
        ),
    ) -> None:

        self._indicator_research_execution_service = (
            indicator_research_execution_service
        )

    def create(
        self,
    ) -> HybridMarketSignalProvider:

        indicator_provider = (
            IndicatorMarketSignalProvider(
                research_execution_service=(
                    self
                    ._indicator_research_execution_service
                ),
            )
        )

        simple_provider = (
            SimpleMarketSignalProvider()
        )

        return HybridMarketSignalProvider(
            indicator_provider=indicator_provider,
            simple_provider=simple_provider,
        )