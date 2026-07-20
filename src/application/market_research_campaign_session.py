from __future__ import annotations

from dataclasses import dataclass

from src.research.research_context import (
    ResearchContext,
)
from src.application.prepared_market_campaign_executor import (
    PreparedMarketCampaignExecutor,
)
from src.research import ( 
    Experiment, 
    Hypothesis, 
    Question,
) 

from src.research.research_campaign import ( 
    ResearchCampaign, 
)

@dataclass(frozen=True, slots=True)
class MarketResearchCampaignSession:
    """
    Immutable prepared campaign session.
    """

    contexts: tuple[
        ResearchContext,
        ...,
    ]

    question: Question

    hypothesis: Hypothesis

    campaign: ResearchCampaign

    experiments: tuple[
        Experiment,
        ...,
    ]

    executor: PreparedMarketCampaignExecutor

