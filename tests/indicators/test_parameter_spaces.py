import pytest

from src.indicators.parameter_spaces import (
    FloatParameter,
    IntegerParameter,
)


def test_integer_parameter_accepts_valid_range() -> None:
    parameter = IntegerParameter(
        minimum=2,
        maximum=100,
        default=14,
    )

    assert parameter.minimum == 2
    assert parameter.maximum == 100
    assert parameter.default == 14
    assert parameter.contains(2)
    assert parameter.contains(14)
    assert parameter.contains(100)
    assert not parameter.contains(1)
    assert not parameter.contains(101)


def test_integer_parameter_rejects_reversed_range() -> None:
    with pytest.raises(
        ValueError,
        match="minimum must not be greater",
    ):
        IntegerParameter(
            minimum=100,
            maximum=2,
            default=14,
        )


def test_integer_parameter_rejects_default_outside_range() -> None:
    with pytest.raises(
        ValueError,
        match="default must be inside",
    ):
        IntegerParameter(
            minimum=2,
            maximum=100,
            default=101,
        )


@pytest.mark.parametrize(
    "field_values",
    [
        {"minimum": True, "maximum": 100, "default": 14},
        {"minimum": 2, "maximum": False, "default": 14},
        {"minimum": 2, "maximum": 100, "default": True},
        {"minimum": 2.0, "maximum": 100, "default": 14},
    ],
)
def test_integer_parameter_rejects_non_integer_values(
    field_values: dict[str, object],
) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        IntegerParameter(**field_values)  # type: ignore[arg-type]


def test_float_parameter_accepts_integer_and_float_input() -> None:
    parameter = FloatParameter(
        minimum=-100,
        maximum=0.0,
        default=-80,
    )

    assert parameter.minimum == -100.0
    assert parameter.maximum == 0.0
    assert parameter.default == -80.0
    assert parameter.contains(-100.0)
    assert parameter.contains(-80.0)
    assert parameter.contains(0.0)


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_float_parameter_rejects_non_finite_values(
    value: float,
) -> None:
    with pytest.raises(ValueError, match="must be finite"):
        FloatParameter(
            minimum=-100.0,
            maximum=0.0,
            default=value,
        )


def test_parameter_spaces_are_immutable() -> None:
    parameter = IntegerParameter(
        minimum=2,
        maximum=100,
        default=14,
    )

    with pytest.raises(AttributeError):
        parameter.default = 20  # type: ignore[misc]