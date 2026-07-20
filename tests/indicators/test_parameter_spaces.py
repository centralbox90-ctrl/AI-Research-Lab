import pytest

from src.indicators.parameter_spaces import (
    ChoiceParameter,
    FloatParameter,
    IntegerParameter,
    ParameterSpaceContract,
)


def test_choice_parameter_accepts_declared_value() -> None:
    parameter = ChoiceParameter(
        values=(
            "cross_above",
            "cross_below",
        ),
        default="cross_above",
    )

    assert parameter.contains("cross_above")
    assert parameter.contains("cross_below")


def test_choice_parameter_rejects_unknown_value() -> None:
    parameter = ChoiceParameter(
        values=(
            "cross_above",
            "cross_below",
        ),
        default="cross_above",
    )

    assert not parameter.contains("touch")
    assert not parameter.contains(None)


def test_choice_parameter_requires_values() -> None:
    with pytest.raises(
        ValueError,
        match="at least one value",
    ):
        ChoiceParameter(
            values=(),
            default="cross_above",
        )


def test_choice_parameter_requires_unique_values() -> None:
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        ChoiceParameter(
            values=(
                "cross_above",
                "cross_above",
            ),
            default="cross_above",
        )


def test_choice_parameter_requires_valid_default() -> None:
    with pytest.raises(
        ValueError,
        match="default must be one",
    ):
        ChoiceParameter(
            values=(
                "cross_above",
                "cross_below",
            ),
            default="touch",
        )


@pytest.mark.parametrize(
    "parameter",
    [
        IntegerParameter(
            minimum=10,
            maximum=20,
            default=14,
        ),
        FloatParameter(
            minimum=-100.0,
            maximum=0.0,
            default=-20.0,
        ),
        ChoiceParameter(
            values=(
                "cross_above",
                "cross_below",
            ),
            default="cross_above",
        ),
    ],
)
def test_parameter_spaces_implement_contract(
    parameter: object,
) -> None:
    assert isinstance(
        parameter,
        ParameterSpaceContract,
    )


def test_integer_parameter_rejects_wrong_type() -> None:
    parameter = IntegerParameter(
        minimum=10,
        maximum=20,
        default=14,
    )

    assert not parameter.contains(True)
    assert not parameter.contains(14.0)
    assert not parameter.contains("14")


def test_float_parameter_rejects_wrong_type() -> None:
    parameter = FloatParameter(
        minimum=-100.0,
        maximum=0.0,
        default=-20.0,
    )

    assert not parameter.contains(True)
    assert not parameter.contains("-20")
    assert not parameter.contains(float("nan"))