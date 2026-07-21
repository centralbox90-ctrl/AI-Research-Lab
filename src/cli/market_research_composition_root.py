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
from src.application.indicator_research_execution_factory import (
    IndicatorResearchExecutionFactory,
)
from src.indicators.catalog import (
    IndicatorCatalog,
)
from src.indicators.discovery import (
    discover_indicators,
)

from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)
from src.application.market_signal_provider_factory import (
    MarketSignalProviderFactory,
)

def build_default_market_research_application(
) -> RunMarketResearch:
    """
    Build the default local market-research application.

    Composition root:
    connects infrastructure, plugins,
    discovery mechanisms and application services.
    """

    store = SqliteResearchCycleStore(
        db_path=RESEARCH_CYCLE_DATABASE_PATH,
    )

    indicator_catalog = IndicatorCatalog(
        discover_indicators(),
    )

    indicator_research_execution_service = (
        IndicatorResearchExecutionFactory(
            indicator_catalog=indicator_catalog,
        ).create()
    )
    
    signal_provider = (
        MarketSignalProviderFactory(
            indicator_research_execution_service=(
                indicator_research_execution_service
            ),
        ).create()
    )
    
    return build_market_research_application(
        data_provider=GeneratedMarketDataProvider(),
        signal_provider=signal_provider,
        store=store,
    )