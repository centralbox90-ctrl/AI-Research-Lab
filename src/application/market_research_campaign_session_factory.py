from __future__ import annotations

from collections.abc import Sequence

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_mapper import (
    MarketExperimentMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_campaign_session import (
    MarketResearchCampaignSession,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.application.prepared_market_backtest_executor import (
    PreparedMarketBacktestExecutor,
)
from src.application.prepared_market_campaign_executor import (
    PreparedMarketCampaignExecutor,
)


class MarketResearchCampaignSessionFactory:
    """
    Creates one immutable campaign session.
    """

    def __init__(
        self,
        *,
        data_provider: MarketDataProvider,
        signal_provider: MarketSignalProvider,
        context_factory: MarketResearchContextFactory,
        mapper: MarketExperimentMapper | None = None,
    ) -> None:
        self._data_provider = data_provider
        self._signal_provider = signal_provider
        self._context_factory = context_factory
        self._mapper = (
            mapper
            or MarketExperimentMapper()
        )

    def create(
        self,
        specifications: Sequence[
            MarketExperimentSpecification
        ],
    ) -> MarketResearchCampaignSession:
        raise NotImplementedError