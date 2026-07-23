from __future__ import annotations

import pandas as pd

from src.indicators.series import IndicatorSeries
from src.indicators.specification import (
    IndicatorSpecification,
)
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


def calculate(
    data: pd.DataFrame,
    specification: IndicatorSpecification,
) -> IndicatorSeries:

    period = int(
        specification.parameters["period"]
    )

    if "close" not in data.columns:
        raise ValueError(
            "RSI requires column: close"
        )

    if period < 1:
        raise ValueError(
            "RSI period must be greater than zero"
        )

    delta = data["close"].diff()

    gain = (
        delta
        .where(delta > 0, 0)
        .rolling(period)
        .mean()
    )

    loss = (
        -delta
        .where(delta < 0, 0)
        .rolling(period)
        .mean()
    )

    rs = gain / loss

    rsi = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )

    return IndicatorSeries.create(
        specification=specification,
        timestamps=data.index,
        values=rsi,
        warmup_bars=period - 1,
    )


RESEARCH_SPACE = IndicatorResearchSpace(
    outputs=(
        IndicatorOutput(
            name="rsi",
        ),
    ),

    calculation_parameters={
        "period": IntegerParameter(
            minimum=5,
            maximum=30,
            default=14,
        ),
    },

    observation_parameters={
        "level": FloatParameter(
            minimum=0.0,
            maximum=100.0,
            default=30.0,
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

    signal_rule_ids=(
        "indicator_direction",
    ),
)


INDICATOR = IndicatorDescriptor(
    id="rsi",
    symbol="RSI",
    name="Relative Strength Index",
    version=1,

    calculator=calculate,

    default_parameters={
        "period": 14,
    },

    research_space=RESEARCH_SPACE,
)