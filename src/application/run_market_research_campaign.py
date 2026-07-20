from __future__ import annotations

from collections.abc import Sequence

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_campaign_session_factory import (
    MarketResearchCampaignSessionFactory,
)
from src.research.engine import (
    ResearchEngine,
)
from src.research.cycle_results import ( 
    ResearchCycleResult, 
)

class RunMarketResearchCampaign:
    def __init__(
        self,
        session_factory: MarketResearchCampaignSessionFactory,
        engine: ResearchEngine | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._engine = engine or ResearchEngine()

    def run(
        self,
        specifications: Sequence[
            MarketExperimentSpecification
        ],
    ) -> list[ResearchCycleResult]:
        session = self._session_factory.create(
            specifications
        )

        return self._engine.run_campaign(
            question=session.question,
            hypothesis=session.hypothesis,
            campaign=session.campaign,
            experiments=list(
                session.experiments
            ),
            executor=session.executor,
        )
