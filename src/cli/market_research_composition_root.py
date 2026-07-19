from __future__ import annotations

from src.application.generated_market_data_provider import (
    GeneratedMarketDataProvider,
)
from src.application.market_research_application import (
    build_market_research_application,
)
from src.application.run_market_research import (
    RunMarketResearch,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


def build_default_market_research_application(
) -> RunMarketResearch:
    """
    Build the default local market-research application.

    This module is the composition root where application services
    are connected to concrete infrastructure adapters.
    """

    store = SqliteResearchCycleStore(
        db_path=RESEARCH_CYCLE_DATABASE_PATH,
    )

    return build_market_research_application(
        data_provider=GeneratedMarketDataProvider(),
        signal_provider=SimpleMarketSignalProvider(),
        store=store,
    )