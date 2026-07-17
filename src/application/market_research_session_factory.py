from __future__ import annotations

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_mapper import (
    MarketExperimentMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_research_session import (
    MarketResearchSession,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.application.prepared_market_backtest_executor import (
    PreparedMarketBacktestExecutor,
)


class MarketResearchSessionFactory:
    """
    Builds one complete market research execution session.

    Market data is loaded exactly once. The same dataset is used both
    for ResearchContext construction and experiment execution.
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
        self._mapper = mapper or MarketExperimentMapper()

    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> MarketResearchSession:
        mapped = self._mapper.map(
            specification,
        )

        market_data = self._data_provider.load(
            specification,
        )

        context = self._context_factory.create(
            specification=specification,
            market_data=market_data,
        )

        executor = PreparedMarketBacktestExecutor(
            specification=specification,
            market_data=market_data,
            signal_provider=self._signal_provider,
        )

        return MarketResearchSession(
            context=context,
            question=mapped.question,
            hypothesis=mapped.hypothesis,
            experiment=mapped.experiment,
            executor=executor,
        )