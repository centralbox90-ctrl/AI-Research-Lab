from src.indicators.implementations.williams_r import INDICATOR
from src.indicators.parameter_spaces import (
    FloatParameter,
    IntegerParameter,
)


def test_indicator_declares_parameter_search_space() -> None:
    research_space = INDICATOR.research_space

    assert research_space is not None
    assert research_space.observation_types == (
        "band_reentry",
    )

    period = research_space.calculation_parameters["period"]
    lower = research_space.observation_parameters["lower_level"]
    upper = research_space.observation_parameters["upper_level"]

    assert isinstance(period, IntegerParameter)
    assert period.grid_values() == tuple(range(10, 18))
    assert isinstance(lower, FloatParameter)
    assert lower.grid_values()[0] == -90.0
    assert lower.grid_values()[-1] == -60.0
    assert isinstance(upper, FloatParameter)
    assert upper.grid_values()[0] == -40.0
    assert upper.grid_values()[-1] == -10.0
