from src.application.mappers.indicator_specification_mapper import (
    IndicatorSpecificationMapper,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


def test_maps_research_specification_to_indicator_specification() -> None:
    research_specification = ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="williams_r",
            indicator_version=1,
        ),
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "level": -20.0,
            "direction": "cross_below",
        },
    )

    mapper = IndicatorSpecificationMapper()

    result = mapper.map(
        research_specification,
    )

    assert result.indicator_type == "williams_r"
    assert result.version == 1
    assert result.parameters == {
        "period": 14,
    }