from dataclasses import FrozenInstanceError

import pytest

from src.research.horizon_comparison import (
    HorizonComparison,
)


def build_comparison(
    **changes: object,
) -> HorizonComparison:
    values = {
        "horizon": 10,
        "candidate_sample_size": 25,
        "baseline_sample_size": 100,
        "mean_return_difference": 0.02,
        "median_return_difference": 0.01,
        "positive_rate_difference": 0.15,
    }
    values.update(changes)

    return HorizonComparison(**values)


def test_stores_normalized_comparison() -> None:
    comparison = build_comparison(
        mean_return_difference=1,
        median_return_difference=0,
        positive_rate_difference=-1,
    )

    assert comparison.horizon == 10
    assert comparison.candidate_sample_size == 25
    assert comparison.baseline_sample_size == 100
    assert comparison.mean_return_difference == 1.0
    assert comparison.median_return_difference == 0.0
    assert comparison.positive_rate_difference == -1.0


def test_is_immutable() -> None:
    comparison = build_comparison()

    with pytest.raises(FrozenInstanceError):
        comparison.horizon = 20


@pytest.mark.parametrize(
    "field_name",
    (
        "horizon",
        "candidate_sample_size",
        "baseline_sample_size",
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
        build_comparison(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "horizon",
        "candidate_sample_size",
        "baseline_sample_size",
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
        build_comparison(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_return_difference",
        "median_return_difference",
        "positive_rate_difference",
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
def test_rejects_non_numeric_differences(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be a real number"
        ),
    ):
        build_comparison(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_return_difference",
        "median_return_difference",
        "positive_rate_difference",
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
def test_rejects_non_finite_differences(
    field_name: str,
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be finite",
    ):
        build_comparison(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        -1.01,
        1.01,
    ),
)
def test_rejects_positive_rate_difference_outside_range(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "positive_rate_difference must be "
            "between minus one and one"
        ),
    ):
        build_comparison(
            positive_rate_difference=invalid_value,
        )
