from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.cli.indicator_comparative_research_composition_root import (
    build_default_indicator_comparative_research_service,
)


def test_builds_default_comparative_research_service(
) -> None:
    service = (
        build_default_indicator_comparative_research_service()
    )

    assert isinstance(
        service,
        IndicatorComparativeResearchService,
    )
