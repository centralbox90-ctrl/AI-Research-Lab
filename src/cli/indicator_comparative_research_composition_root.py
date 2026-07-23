from __future__ import annotations

from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
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


def build_default_indicator_comparative_research_service(
) -> IndicatorComparativeResearchService:
    """Build the default comparative research service."""

    indicator_catalog = _build_indicator_catalog()

    return _build_indicator_comparative_research_service(
        indicator_catalog
    )


def build_default_indicator_comparative_research_application(
    *,
    data_provider: CanonicalMarketDatasetProvider,
) -> IndicatorComparativeResearchApplication:
    """Build the default comparative research application."""

    indicator_catalog = _build_indicator_catalog()

    return IndicatorComparativeResearchApplication(
        data_provider=data_provider,
        indicator_catalog=indicator_catalog,
        research_service=(
            _build_indicator_comparative_research_service(
                indicator_catalog
            )
        ),
    )


def _build_indicator_catalog() -> IndicatorCatalog:
    return IndicatorCatalog(
        discover_indicators(),
    )


def _build_indicator_comparative_research_service(
    indicator_catalog: IndicatorCatalog,
) -> IndicatorComparativeResearchService:
    research_execution_service = (
        IndicatorResearchExecutionFactory(
            indicator_catalog=indicator_catalog,
        ).create()
    )

    return IndicatorComparativeResearchService(
        research_execution_service=(
            research_execution_service
        ),
    )
