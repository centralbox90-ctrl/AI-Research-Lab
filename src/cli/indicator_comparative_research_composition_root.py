from __future__ import annotations

from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
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
    """
    Build the default comparative indicator research service.
    """

    indicator_catalog = IndicatorCatalog(
        discover_indicators(),
    )

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
