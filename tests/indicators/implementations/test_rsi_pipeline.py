import pandas as pd

from src.application.indicator_research_execution_factory import (
    IndicatorResearchExecutionFactory,
)
from src.indicators.catalog import IndicatorCatalog
from src.indicators.discovery import discover_indicators
from src.indicators.implementations.rsi import INDICATOR
from src.research.specification_factory import (
    create_default_research_specification,
)


def test_rsi_default_specification_executes_complete_pipeline(
) -> None:
    catalog = IndicatorCatalog(
        discover_indicators()
    )
    specification = (
        create_default_research_specification(
            INDICATOR
        )
    )
    service = IndicatorResearchExecutionFactory(
        indicator_catalog=catalog,
    ).create()

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
        }
    )

    result = service.execute(
        data=data,
        specification=specification,
    )

    assert specification.calculation_parameter_values == {
        "period": 14,
    }
    assert specification.observation_parameter_values == {
        "level": 30.0,
        "direction": "cross_below",
    }
    assert len(result.series) == len(data)
    assert len(result.observations) == len(data)
    assert set(result.observations).issubset({-1, 0, 1})
    assert -1 in result.observations
