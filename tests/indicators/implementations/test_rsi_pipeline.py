import pandas as pd

from src.indicators.catalog import IndicatorCatalog
from src.indicators.discovery import discover_indicators
from src.indicators.calculation_service import (
    IndicatorCalculationService,
)
from src.application.mappers.indicator_specification_mapper import (
    IndicatorSpecificationMapper,
)
from src.research.specification import (
    ResearchSpecification,
    IndicatorReference,
)


def test_rsi_calculation_pipeline():

    catalog = IndicatorCatalog(
        discover_indicators()
    )

    service = IndicatorCalculationService(
        catalog
    )

    research_specification = (
        ResearchSpecification.create(
            indicator=IndicatorReference(
                indicator_id="rsi",
                indicator_version=1,
            ),
            output="rsi",
            profile="overbought_oversold",
            observation_type="level_cross",
            signal_rule_id="indicator_direction",
            calculation_parameters={
                "period": 14,
            },
            observation_parameters={},
        )
    )

    indicator_specification = (
        IndicatorSpecificationMapper()
        .map(research_specification)
    )

    data = pd.DataFrame(
        {
            "close": [
                100,
                101,
                102,
                103,
                102,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
            ]
        }
    )

    result = service.calculate(
        data,
        indicator_specification,
    )

    assert len(result.values) == len(data)