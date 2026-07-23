from dataclasses import FrozenInstanceError

import pytest

from src.research.horizon_statistics import (
    HorizonStatistics,
)


def build_statistics(
    **changes: object,
) -> HorizonStatistics:
    values = {
        "horizon": 5,
        "sample_size": 10,
        "mean_return": 0.02,
        "median_return": 0.01,
        "positive_rate": 0.6,
        "minimum_return": -0.05,
        "maximum_return": 0.08,
    }
    values.update(changes)

    return HorizonStatistics(**values)


def test_stores_normalized_statistics() -> None:
    statistics = build_statistics(
        mean_return=1,
        median_return=0,
        positive_rate=1,
        minimum_return=-1,
        maximum_return=2,
    )

    assert statistics.horizon == 5
    assert statistics.sample_size == 10
    assert statistics.mean_return == 1.0
    assert statistics.median_return == 0.0
    assert statistics.positive_rate == 1.0
    assert statistics.minimum_return == -1.0
    assert statistics.maximum_return == 2.0


def test_is_immutable() -> None:
    statistics = build_statistics()

    with pytest.raises(FrozenInstanceError):
        statistics.sample_size = 20


@pytest.mark.parametrize(
    "field_name",
    (
        "horizon",
        "sample_size",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        True,
        1.5,
        "1",
    ),
)
def test_rejects_invalid_integer_fields(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        build_statistics(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "horizon",
        "sample_size",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        0,
        -1,
    ),
)
def test_rejects_non_positive_integer_fields(
    field_name: str,
    invalid_value: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be positive",
    ):
        build_statistics(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_return",
        "median_return",
        "positive_rate",
        "minimum_return",
        "maximum_return",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        True,
        "0.1",
        object(),
    ),
)
def test_rejects_non_numeric_statistics(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be a real number"
        ),
    ):
        build_statistics(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_return",
        "median_return",
        "positive_rate",
        "minimum_return",
        "maximum_return",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_rejects_non_finite_statistics(
    field_name: str,
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be finite",
    ):
        build_statistics(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        -0.01,
        1.01,
    ),
)
def test_rejects_positive_rate_outside_unit_interval(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "positive_rate must be between "
            "zero and one"
        ),
    ):
        build_statistics(
            positive_rate=invalid_value,
        )


def test_rejects_reversed_return_range() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "minimum_return must not exceed "
            "maximum_return"
        ),
    ):
        build_statistics(
            minimum_return=0.1,
            maximum_return=0.0,
        )


@pytest.mark.parametrize(
    "median_return",
    (
        -0.06,
        0.09,
    ),
)
def test_rejects_median_outside_return_range(
    median_return: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "median_return must be within "
            "the return range"
        ),
    ):
        build_statistics(
            median_return=median_return,
        )


@pytest.mark.parametrize(
    "mean_return",
    (
        -0.06,
        0.09,
    ),
)
def test_rejects_mean_outside_return_range(
    mean_return: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "mean_return must be within "
            "the return range"
        ),
    ):
        build_statistics(
            mean_return=mean_return,
        )
