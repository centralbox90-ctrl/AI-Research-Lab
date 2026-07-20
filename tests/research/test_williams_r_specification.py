from __future__ import annotations

from src.indicators.implementations.williams_r import (
    INDICATOR,
)
from src.research.specification_factory import (
    create_research_specification,
)


def test_williams_r_research_specification():
    specification = create_research_specification(
        INDICATOR,
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "level": -80.0,
        },
    )

    assert (
        specification.indicator.indicator_id
        == "williams_r"
    )
    assert (
        specification.indicator.indicator_version
        == 1
    )
    assert specification.output == "williams_r"
    assert (
        specification.calculation_parameter_values
        == {
            "period": 14,
        }
    )
    assert (
        specification.observation_parameter_values
        == {
            "direction": "cross_below",
            "level": -80.0,
        }
    )


def test_williams_r_direction_can_be_overridden():
    specification = create_research_specification(
        INDICATOR,
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "level": -80.0,
            "direction": "cross_above",
        },
    )

    assert (
        specification.observation_parameter_values
        == {
            "direction": "cross_above",
            "level": -80.0,
        }
    )


def test_williams_r_direction_can_be_overridden():
    specification = create_research_specification(
        INDICATOR,
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "level": -80.0,
            "direction": "cross_above",
        },
    )

    assert (
        specification.observation_parameter_values
        == {
            "direction": "cross_above",
            "level": -80.0,
        }
    )
