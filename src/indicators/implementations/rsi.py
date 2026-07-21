from __future__ import annotations

import pandas as pd

from src.indicators.series import IndicatorSeries
from src.indicators.descriptor import IndicatorDescriptor
from src.indicators.parameter_spaces import (
    IntegerParameter,
)
from src.indicators.research_space import (
    IndicatorOutput,
    IndicatorResearchSpace,
)


def calculate(
    data: pd.DataFrame,
    specification,
) -> IndicatorSeries:

    period = int(
        specification.parameters["period"]
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
        warmup_bars=period,
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

    observation_parameters={},

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