from src.indicators.implementations.williams_r import INDICATOR
from src.research.specification_factory import (
    create_research_specification,
)
from src.research.specification_grid import (
    ResearchSpecificationGridFactory,
)


def test_williams_r_research_specification() -> None:
    specification = create_research_specification(
        INDICATOR,
        calculation_parameters={"period": 12},
        observation_parameters={
            "lower_level": -70.0,
            "upper_level": -30.0,
        },
    )

    assert specification.indicator.indicator_id == "williams_r"
    assert specification.observation_type == "band_reentry"
    assert specification.calculation_parameter_values == {
        "period": 12,
    }
    assert specification.observation_parameter_values == {
        "lower_level": -70.0,
        "upper_level": -30.0,
    }


def test_williams_r_grid_contains_every_declared_combination() -> None:
    specifications = ResearchSpecificationGridFactory().create(
        INDICATOR
    )

    assert len(specifications) == 8 * 31 * 31
    assert any(
        specification.calculation_parameter_values["period"] == 12
        and specification.observation_parameter_values == {
            "lower_level": -70.0,
            "upper_level": -30.0,
        }
        for specification in specifications
    )
