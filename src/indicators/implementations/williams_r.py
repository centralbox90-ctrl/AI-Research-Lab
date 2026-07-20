from __future__ import annotations

from src.indicators.descriptor import IndicatorDescriptor
from src.indicators.parameter_spaces import (
    ChoiceParameter,
    FloatParameter,
    IntegerParameter,
)
from src.indicators.research_space import (
    IndicatorOutput,
    IndicatorResearchSpace,
)


def calculate_williams_r(
    data,
    specification,
):
    raise NotImplementedError(
        "Williams %R calculation is not implemented yet."
    )


RESEARCH_SPACE = IndicatorResearchSpace(
    outputs=(
        IndicatorOutput(
            name="williams_r",
        ),
    ),
    calculation_parameters={
        "period": IntegerParameter(
            minimum=10,
            maximum=17,
            default=14,
        ),
    },
    observation_parameters={
        "level": FloatParameter(
            minimum=-100.0,
            maximum=0.0,
            default=-20.0,
        ),
        "direction": ChoiceParameter(
            values=(
                "cross_above",
                "cross_below",
            ),
            default="cross_below",
        ),
    },
    observation_types=(
        "level_cross",
    ),
    research_profiles=(
        "overbought_oversold",
    ),
)


INDICATOR = IndicatorDescriptor(
    id="williams_r",
    symbol="%R",
    name="Williams %R",
    version=1,
    calculator=calculate_williams_r,
    default_parameters={
        "period": 14,
    },
    research_space=RESEARCH_SPACE,
)