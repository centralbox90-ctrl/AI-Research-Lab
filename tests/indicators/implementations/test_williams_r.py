from src.indicators.implementations.williams_r import (
    INDICATOR,
)
from src.indicators.parameter_spaces import (
    ChoiceParameter,
)


def test_indicator_declares_research_space() -> None:
    assert INDICATOR.research_space is not None


def test_indicator_supports_level_cross() -> None:
    research_space = INDICATOR.research_space

    assert research_space is not None
    assert research_space.observation_types == (
        "level_cross",
    )


def test_indicator_declares_direction_parameter() -> None:
    research_space = INDICATOR.research_space

    assert research_space is not None

    direction = research_space.observation_parameters[
        "direction"
    ]

    assert isinstance(
        direction,
        ChoiceParameter,
    )

    assert direction.values == (
        "cross_above",
        "cross_below",
    )

    assert direction.default == "cross_below"