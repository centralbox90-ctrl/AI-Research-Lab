from __future__ import annotations

from dataclasses import dataclass

from src.application.market_research_context import (
    MarketResearchContext,
)
from src.application.prepared_market_campaign_executor import (
    PreparedMarketCampaignExecutor,
)
from src.research import (
    Experiment,
    Hypothesis,
    Question,
)


@dataclass(frozen=True, slots=True)
class MarketResearchCampaignSession:
    """
    Immutable prepared campaign session.
    """

    contexts: tuple[
        MarketResearchContext,
        ...,
    ]

    question: Question

    hypothesis: Hypothesis

    experiments: tuple[
        Experiment,
        ...,
    ]

    executor: PreparedMarketCampaignExecutor