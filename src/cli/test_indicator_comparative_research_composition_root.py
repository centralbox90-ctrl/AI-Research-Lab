import pandas as pd

from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.cli.indicator_comparative_research_composition_root import (
    build_default_indicator_comparative_research_service,
)
from src.indicators.implementations.rsi import INDICATOR
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification_factory import (
    create_default_research_specification,
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


def test_runs_default_rsi_comparative_pipeline(
) -> None:
    service = (
        build_default_indicator_comparative_research_service()
    )
    specification = (
        create_default_research_specification(
            INDICATOR
        )
    )
    design = IndicatorComparativeResearchDesign(
        research_specification=specification,
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=(1, 3),
            )
        ),
    )

    close = (
        [
            100.0 + index
            for index in range(20)
        ]
        + [
            120.0 - (2.0 * index)
            for index in range(20)
        ]
    )
    data = pd.DataFrame(
        {
            "close": close,
        },
        index=pd.date_range(
            "2026-01-01",
            periods=len(close),
            freq="h",
            tz="UTC",
        ),
    )

    analysis = service.run(
        data=data,
        design=design,
        symbol="EURUSD",
        timeframe="H1",
    )

    assert (
        analysis.candidate_result
        .observation_count
        >= 1
    )
    assert (
        analysis.baseline_result
        .observation_count
        == len(data) - 3
    )
    assert tuple(
        comparison.horizon
        for comparison in analysis.comparisons
    ) == (1, 3)
