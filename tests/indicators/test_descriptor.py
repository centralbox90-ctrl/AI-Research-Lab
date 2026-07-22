import pandas as pd
import pytest

from src.indicators.descriptor import (
    IndicatorDescriptor,
    IntegerParameterSpace,
    LevelCrossResearchProfile,
    NumericParameterSpace,
)
from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification


def stub_calculator(
    data: pd.DataFrame,
    specification: IndicatorSpecification,
) -> IndicatorSeries:
    raise NotImplementedError


def test_creates_indicator_descriptor() -> None:
    descriptor = IndicatorDescriptor(
        id="williams_r",
        symbol="WILLR",
        name="Williams %R",
        version=1,
        calculator=stub_calculator,
        default_parameters={
            "period": 14,
        },
        parameter_spaces={
            "period": IntegerParameterSpace(
                minimum=5,
                maximum=50,
                step=1,
                default=14,
                coarse_values=(
                    5,
                    8,
                    11,
                    14,
                    17,
                    20,
                    25,
                    30,
                    40,
                    50,
                ),
            ),
        },
        research_profiles=(
            LevelCrossResearchProfile(
                level_space=NumericParameterSpace(
                    minimum=-95.0,
                    maximum=-5.0,
                    step=5.0,
                    coarse_values=(
                        -90.0,
                        -70.0,
                        -50.0,
                        -30.0,
                        -10.0,
                    ),
                ),
                canonical_levels=(
                    -80.0,
                    -20.0,
                ),
            ),
        ),
    )

    assert descriptor.id == "williams_r"
    assert descriptor.symbol == "WILLR"
    assert descriptor.default_parameters["period"] == 14

    period_space = descriptor.parameter_spaces["period"]

    assert period_space.minimum == 5
    assert period_space.maximum == 50

    profile = descriptor.research_profiles[0]

    assert profile.canonical_levels == (
        -80.0,
        -20.0,
    )


def test_normalizes_descriptor_metadata() -> None:
    descriptor = IndicatorDescriptor(
        id="  williams_r  ",
        symbol="  WILLR  ",
        name="  Williams %R  ",
        version=1,
        calculator=stub_calculator,
    )

    assert descriptor.id == "williams_r"
    assert descriptor.symbol == "WILLR"
    assert descriptor.name == "Williams %R"


@pytest.mark.parametrize(
    ("field_name", "field_value", "error_message"),
    (
        ("id", "   ", "id must not be empty"),
        ("symbol", "   ", "symbol must not be empty"),
        ("name", "   ", "name must not be empty"),
    ),
)
def test_rejects_empty_descriptor_metadata(
    field_name: str,
    field_value: str,
    error_message: str,
) -> None:
    arguments = {
        "id": "williams_r",
        "symbol": "WILLR",
        "name": "Williams %R",
        "version": 1,
        "calculator": stub_calculator,
    }
    arguments[field_name] = field_value

    with pytest.raises(ValueError, match=error_message):
        IndicatorDescriptor(**arguments)


@pytest.mark.parametrize("version", [0, -1])
def test_rejects_non_positive_version(
    version: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="version must be greater than zero",
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=version,
            calculator=stub_calculator,
        )


def test_rejects_boolean_version() -> None:
    with pytest.raises(
        TypeError,
        match="version must be an integer",
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=True,
            calculator=stub_calculator,
        )


def test_rejects_non_callable_calculator() -> None:
    with pytest.raises(
        TypeError,
        match="calculator must be callable",
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=object(),
        )


def test_rejects_unsupported_parameter_space_type() -> None:
    with pytest.raises(
        TypeError,
        match="unsupported type",
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=stub_calculator,
            parameter_spaces={
                "period": object(),
            },
        )


def test_rejects_empty_parameter_space_name() -> None:
    with pytest.raises(
        ValueError,
        match="parameter space name must not be empty",
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=stub_calculator,
            parameter_spaces={
                "   ": IntegerParameterSpace(
                    minimum=5,
                    maximum=50,
                    step=1,
                    default=14,
                ),
            },
        )


def test_rejects_default_without_matching_parameter_space() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "default parameters do not have matching "
            "parameter spaces: smoothing"
        ),
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=stub_calculator,
            default_parameters={
                "period": 14,
                "smoothing": 3,
            },
            parameter_spaces={
                "period": IntegerParameterSpace(
                    minimum=5,
                    maximum=50,
                    step=1,
                    default=14,
                ),
            },
        )


def test_rejects_default_that_differs_from_parameter_space() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "default parameter 'period' does not match "
            "its parameter space default"
        ),
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=stub_calculator,
            default_parameters={
                "period": 20,
            },
            parameter_spaces={
                "period": IntegerParameterSpace(
                    minimum=5,
                    maximum=50,
                    step=1,
                    default=14,
                ),
            },
        )


def test_rejects_unsupported_research_space_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "research_space must be an "
            "IndicatorResearchSpace or None"
        ),
    ):
        IndicatorDescriptor(
            id="williams_r",
            symbol="WILLR",
            name="Williams %R",
            version=1,
            calculator=stub_calculator,
            research_space=object(),
        )


def test_rejects_canonical_level_outside_space() -> None:
    with pytest.raises(
        ValueError,
        match="canonical levels",
    ):
        LevelCrossResearchProfile(
            level_space=NumericParameterSpace(
                minimum=-95.0,
                maximum=-5.0,
                step=5.0,
            ),
            canonical_levels=(
                -100.0,
            ),
        )


def test_rejects_duplicate_canonical_levels() -> None:
    with pytest.raises(
        ValueError,
        match="canonical levels must not contain duplicates",
    ):
        LevelCrossResearchProfile(
            level_space=NumericParameterSpace(
                minimum=-95.0,
                maximum=-5.0,
                step=5.0,
            ),
            canonical_levels=(
                -80.0,
                -80.0,
            ),
        )


def test_rejects_invalid_direction() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported directions",
    ):
        LevelCrossResearchProfile(
            level_space=NumericParameterSpace(
                minimum=-95.0,
                maximum=-5.0,
                step=5.0,
            ),
            canonical_levels=(
                -80.0,
            ),
            directions=(
                "unknown",
            ),
        )


def test_rejects_duplicate_directions() -> None:
    with pytest.raises(
        ValueError,
        match="directions must not contain duplicates",
    ):
        LevelCrossResearchProfile(
            level_space=NumericParameterSpace(
                minimum=-95.0,
                maximum=-5.0,
                step=5.0,
            ),
            canonical_levels=(-80.0,),
            directions=(
                "cross_above",
                "cross_above",
            ),
        )


def test_accepts_empty_canonical_levels() -> None:
    profile = LevelCrossResearchProfile(
        level_space=NumericParameterSpace(
            minimum=-95.0,
            maximum=-5.0,
            step=5.0,
        ),
        canonical_levels=(),
    )

    assert profile.canonical_levels == ()


def test_descriptor_parameter_spaces_are_immutable() -> None:
    descriptor = IndicatorDescriptor(
        id="williams_r",
        symbol="WILLR",
        name="Williams %R",
        version=1,
        calculator=stub_calculator,
        parameter_spaces={
            "period": IntegerParameterSpace(
                minimum=5,
                maximum=50,
                step=1,
                default=14,
            ),
        },
    )

    with pytest.raises(TypeError):
        descriptor.parameter_spaces["period"] = IntegerParameterSpace(
            minimum=10,
            maximum=100,
            step=1,
            default=20,
        )


def test_descriptor_research_profiles_are_immutable() -> None:
    descriptor = IndicatorDescriptor(
        id="williams_r",
        symbol="WILLR",
        name="Williams %R",
        version=1,
        calculator=stub_calculator,
        research_profiles=(
            LevelCrossResearchProfile(
                level_space=NumericParameterSpace(
                    minimum=-95.0,
                    maximum=-5.0,
                    step=5.0,
                ),
                canonical_levels=(-80.0,),
            ),
        ),
    )

    with pytest.raises(AttributeError):
        descriptor.research_profiles += (
            LevelCrossResearchProfile(
                level_space=NumericParameterSpace(
                    minimum=-95.0,
                    maximum=-5.0,
                    step=5.0,
                ),
                canonical_levels=(-20.0,),
            ),
        )


def test_descriptor_parameters_are_immutable() -> None:
    descriptor = IndicatorDescriptor(
        id="williams_r",
        symbol="WILLR",
        name="Williams %R",
        version=1,
        calculator=stub_calculator,
        default_parameters={
            "period": 14,
        },
    )

    with pytest.raises(TypeError):
        descriptor.default_parameters["period"] = 20