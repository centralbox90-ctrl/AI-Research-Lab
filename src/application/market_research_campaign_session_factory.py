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
from src.research.research_context import (
    ResearchContext,
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
from src.research.research_campaign import ( 
    ResearchCampaign, 
)

class MarketResearchCampaignSessionFactory:
    """
    Creates one immutable prepared market research campaign session.
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
        mapped = self._mapper.map_campaign(
            specifications
        )

        contexts: list[
            ResearchContext
        ] = []

        executors_by_experiment_id: dict[
            str,
            PreparedMarketBacktestExecutor,
        ] = {}

        for specification, experiment in zip(
            specifications,
            mapped.experiments,
            strict=True,
        ):
            dataset = self._data_provider.load(
                specification
            )

            context = self._context_factory.create(
                specification=specification,
                dataset=dataset,
            )

            executor = PreparedMarketBacktestExecutor(
                specification=specification,
                market_data=dataset,
                signal_provider=self._signal_provider,
            )

            contexts.append(
                context
            )

            executors_by_experiment_id[
                experiment.id
            ] = executor
        
        campaign = ResearchCampaign(
           title=mapped.question.title,
           hypothesis_id=mapped.hypothesis.id,
        )

        for experiment in mapped.experiments:
           campaign.add_experiment(
               experiment.id,
        )

        campaign_executor = PreparedMarketCampaignExecutor(
            executors_by_experiment_id
        )

        return MarketResearchCampaignSession(
            contexts=tuple(contexts),
            question=mapped.question,
            hypothesis=mapped.hypothesis,
            campaign=campaign,
            experiments=tuple(
                mapped.experiments
            ),
            executor=campaign_executor,
        )






