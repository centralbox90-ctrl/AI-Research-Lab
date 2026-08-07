from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
)
from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
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
        data_provider: CanonicalMarketDatasetProvider,
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

        datasets_by_identity: dict[
            tuple[str, str, str, datetime, datetime],
            CanonicalMarketDataset,
        ] = {}

        for specification, experiment in zip(
            specifications,
            mapped.experiments,
            strict=True,
        ):
            data_identity = self._data_identity(
                specification
            )

            dataset = datasets_by_identity.get(
                data_identity
            )

            if dataset is None:
                dataset = self._data_provider.load(
                    specification
                )
                datasets_by_identity[
                    data_identity
                ] = dataset

            context = self._context_factory.create(
                specification=specification,
                dataset=dataset,
            )

            executor = PreparedMarketBacktestExecutor(
                specification=specification,
                market_data=context.market_data,
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

    @staticmethod
    def _data_identity(
        specification: MarketExperimentSpecification,
    ) -> tuple[str, str, str, datetime, datetime]:
        return (
            specification.data_source.strip().lower(),
            specification.symbol.strip(),
            specification.timeframe.strip(),
            specification.start_at,
            specification.end_at,
        )




