from __future__ import annotations

from src.indicators.series import IndicatorSeries
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
    period = int(specification.parameters["period"])

    required_columns = {"high", "low", "close"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Williams %R requires columns: high, low, close. "
            f"Missing: {missing}"
        )

    if period <= 0:
        raise ValueError(
            "Williams %R period must be greater than zero."
        )

    highest_high = data["high"].rolling(
        window=period,
        min_periods=period,
    ).max()

    lowest_low = data["low"].rolling(
        window=period,
        min_periods=period,
    ).min()

    price_range = highest_high - lowest_low

    values = (
        -100.0
        * (highest_high - data["close"])
        / price_range
    )

    # Защита от деления на ноль, когда high == low
    values = values.where(price_range != 0.0)

    return IndicatorSeries.create(
        specification=specification,
        timestamps=data.index,
        values=values,
        warmup_bars=period - 1,
        source_data_ref=None,
        metadata={
            "indicator": "williams_r",
            "period": period,
        },
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

    signal_rule_ids=(
        "indicator_direction",
    ),
)

INDICATOR = IndicatorDescriptor(
    id="williams_r",
    symbol="%R",
    name="Williams %R",
    version=1,
    calculator=calculate,
    default_parameters={
        "period": 14,
    },
    research_space=RESEARCH_SPACE,
)