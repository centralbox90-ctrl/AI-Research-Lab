import pytest

from src.indicators.parameter_spaces import (
    FloatParameter,
    IntegerParameter,
)
from src.indicators.research_space import (
    IndicatorOutput,
    IndicatorResearchSpace,
)


def create_research_space() -> IndicatorResearchSpace:
    return IndicatorResearchSpace(
        outputs=(
            IndicatorOutput(name="value"),
        ),
        calculation_parameters={
            "period": IntegerParameter(
                minimum=2,
                maximum=100,
                default=14,
            ),
        },
        observation_parameters={
            "threshold": FloatParameter(
                minimum=-100.0,
                maximum=0.0,
                default=-80.0,
            ),
        },
        observation_types=(
            "cross_above",
            "cross_below",
        ),
        research_profiles=(
            "mean_reversion",
            "response_decay",
        ),
    )


def test_research_space_stores_declarations() -> None:
    research_space = create_research_space()

    assert research_space.outputs == (
        IndicatorOutput(name="value"),
    )

    assert (
        research_space.calculation_parameters["period"].default
        == 14
    )
    assert (
        research_space.observation_parameters["threshold"].default
        == -80.0
    )

    assert research_space.observation_types == (
        "cross_above",
        "cross_below",
    )
    assert research_space.research_profiles == (
        "mean_reversion",
        "response_decay",
    )


def test_output_name_is_normalized() -> None:
    output = IndicatorOutput(name="  value  ")

    assert output.name == "value"


def test_output_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="output name must not be empty",
    ):
        IndicatorOutput(name="   ")


def test_research_space_requires_at_least_one_output() -> None:
    with pytest.raises(
        ValueError,
        match="at least one output",
    ):
        IndicatorResearchSpace(
            outputs=(),
            calculation_parameters={},
            observation_parameters={},
            observation_types=(),
            research_profiles=(),
        )


def test_research_space_rejects_duplicate_output_names() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate indicator output names",
    ):
        IndicatorResearchSpace(
            outputs=(
                IndicatorOutput(name="value"),
                IndicatorOutput(name="value"),
            ),
            calculation_parameters={},
            observation_parameters={},
            observation_types=(),
            research_profiles=(),
        )


def test_research_space_rejects_duplicate_observation_types() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate observation type",
    ):
        IndicatorResearchSpace(
            outputs=(
                IndicatorOutput(name="value"),
            ),
            calculation_parameters={},
            observation_parameters={},
            observation_types=(
                "cross_above",
                "cross_above",
            ),
            research_profiles=(),
        )


def test_research_space_rejects_duplicate_research_profiles() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate research profile",
    ):
        IndicatorResearchSpace(
            outputs=(
                IndicatorOutput(name="value"),
            ),
            calculation_parameters={},
            observation_parameters={},
            observation_types=(),
            research_profiles=(
                "mean_reversion",
                "mean_reversion",
            ),
        )


def test_parameter_names_must_be_distinct_between_groups() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicates: period",
    ):
        IndicatorResearchSpace(
            outputs=(
                IndicatorOutput(name="value"),
            ),
            calculation_parameters={
                "period": IntegerParameter(
                    minimum=2,
                    maximum=100,
                    default=14,
                ),
            },
            observation_parameters={
                "period": IntegerParameter(
                    minimum=1,
                    maximum=10,
                    default=2,
                ),
            },
            observation_types=(),
            research_profiles=(),
        )


def test_parameter_mappings_are_immutable() -> None:
    research_space = create_research_space()

    with pytest.raises(TypeError):
        research_space.calculation_parameters["another"] = (
            IntegerParameter(
                minimum=1,
                maximum=10,
                default=5,
            )
        )  # type: ignore[index]


def test_research_space_is_immutable() -> None:
    research_space = create_research_space()

    with pytest.raises(AttributeError):
        research_space.outputs = ()  # type: ignore[misc]


def test_source_parameter_dictionary_is_copied() -> None:
    parameters = {
        "period": IntegerParameter(
            minimum=2,
            maximum=100,
            default=14,
        ),
    }

    research_space = IndicatorResearchSpace(
        outputs=(
            IndicatorOutput(name="value"),
        ),
        calculation_parameters=parameters,
        observation_parameters={},
        observation_types=(),
        research_profiles=(),
    )

    parameters.clear()

    assert "period" in research_space.calculation_parameters