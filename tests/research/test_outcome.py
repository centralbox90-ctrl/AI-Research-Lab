from dataclasses import FrozenInstanceError

import pytest

from src.research.outcome import (
    ForwardReturnOutcome,
)


def make_outcome(
    **overrides: object,
) -> ForwardReturnOutcome:
    values: dict[str, object] = {
        "observation_id": "observation-1",
        "horizon": 5,
        "start_bar_index": 10,
        "start_price": 100.0,
        "end_price": 110.0,
    }
    values.update(overrides)
    return ForwardReturnOutcome(**values)


def test_stores_forward_return_measurement() -> None:
    outcome = make_outcome()

    assert outcome.observation_id == "observation-1"
    assert outcome.horizon == 5
    assert outcome.start_bar_index == 10
    assert outcome.end_bar_index == 15
    assert outcome.start_price == 100.0
    assert outcome.end_price == 110.0
    assert outcome.value == pytest.approx(0.1)


def test_normalizes_observation_id() -> None:
    outcome = make_outcome(
        observation_id="  observation-1  ",
    )

    assert outcome.observation_id == "observation-1"


@pytest.mark.parametrize(
    "observation_id",
    [
        "",
        " ",
        "\t",
        "\n",
    ],
)
def test_rejects_blank_observation_id(
    observation_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="observation_id must not be empty",
    ):
        make_outcome(
            observation_id=observation_id,
        )


def test_rejects_non_string_observation_id() -> None:
    with pytest.raises(
        TypeError,
        match="observation_id must be a string",
    ):
        make_outcome(observation_id=None)


@pytest.mark.parametrize(
    "horizon",
    [
        True,
        False,
        1.0,
        "1",
        None,
    ],
)
def test_rejects_non_integer_horizon(
    horizon: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="horizon must be an integer",
    ):
        make_outcome(horizon=horizon)


@pytest.mark.parametrize(
    "horizon",
    [
        0,
        -1,
        -10,
    ],
)
def test_rejects_non_positive_horizon(
    horizon: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="horizon must be positive",
    ):
        make_outcome(horizon=horizon)


@pytest.mark.parametrize(
    "start_bar_index",
    [
        True,
        False,
        1.0,
        "1",
        None,
    ],
)
def test_rejects_non_integer_start_bar_index(
    start_bar_index: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="start_bar_index must be an integer",
    ):
        make_outcome(
            start_bar_index=start_bar_index,
        )


def test_rejects_negative_start_bar_index() -> None:
    with pytest.raises(
        ValueError,
        match="start_bar_index must not be negative",
    ):
        make_outcome(start_bar_index=-1)


@pytest.mark.parametrize(
    "field_name",
    [
        "start_price",
        "end_price",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        "100",
        None,
    ],
)
def test_rejects_non_numeric_prices(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a real number",
    ):
        make_outcome(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "start_price",
        "end_price",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        0.0,
        -1.0,
    ],
)
def test_rejects_non_positive_prices(
    field_name: str,
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be positive",
    ):
        make_outcome(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "start_price",
        "end_price",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_rejects_non_finite_prices(
    field_name: str,
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be finite",
    ):
        make_outcome(**{field_name: value})


def test_is_immutable() -> None:
    outcome = make_outcome()

    with pytest.raises(FrozenInstanceError):
        outcome.end_price = 120.0
