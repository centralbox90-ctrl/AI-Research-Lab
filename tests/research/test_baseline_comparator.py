import pytest

from src.research.baseline_comparator import (
    BaselineComparator,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)


def build_statistics(
    horizon: int,
    *,
    sample_size: int = 10,
    mean_return: float = 0.0,
    median_return: float = 0.0,
    positive_rate: float = 0.5,
) -> HorizonStatistics:
    return HorizonStatistics(
        horizon=horizon,
        sample_size=sample_size,
        mean_return=mean_return,
        median_return=median_return,
        positive_rate=positive_rate,
        minimum_return=-1.0,
        maximum_return=1.0,
    )


def test_compares_candidate_with_baseline(
) -> None:
    comparisons = BaselineComparator().compare(
        candidate=(
            build_statistics(
                1,
                sample_size=20,
                mean_return=0.05,
                median_return=0.03,
                positive_rate=0.7,
            ),
            build_statistics(
                5,
                sample_size=18,
                mean_return=-0.02,
                median_return=-0.01,
                positive_rate=0.4,
            ),
        ),
        baseline=(
            build_statistics(
                1,
                sample_size=100,
                mean_return=0.01,
                median_return=0.0,
                positive_rate=0.55,
            ),
            build_statistics(
                5,
                sample_size=96,
                mean_return=-0.03,
                median_return=-0.02,
                positive_rate=0.45,
            ),
        ),
    )

    one_bar, five_bars = comparisons

    assert one_bar.horizon == 1
    assert one_bar.candidate_sample_size == 20
    assert one_bar.baseline_sample_size == 100
    assert (
        one_bar.mean_return_difference
        == pytest.approx(0.04)
    )
    assert (
        one_bar.median_return_difference
        == pytest.approx(0.03)
    )
    assert (
        one_bar.positive_rate_difference
        == pytest.approx(0.15)
    )

    assert five_bars.horizon == 5
    assert (
        five_bars.mean_return_difference
        == pytest.approx(0.01)
    )
    assert (
        five_bars.median_return_difference
        == pytest.approx(0.01)
    )
    assert (
        five_bars.positive_rate_difference
        == pytest.approx(-0.05)
    )


def test_matches_baseline_by_horizon(
) -> None:
    comparisons = BaselineComparator().compare(
        candidate=(
            build_statistics(
                5,
                mean_return=0.5,
            ),
            build_statistics(
                1,
                mean_return=0.1,
            ),
        ),
        baseline=(
            build_statistics(
                1,
                mean_return=0.01,
            ),
            build_statistics(
                5,
                mean_return=0.05,
            ),
        ),
    )

    assert tuple(
        comparison.horizon
        for comparison in comparisons
    ) == (5, 1)
    assert (
        comparisons[0].mean_return_difference
        == pytest.approx(0.45)
    )
    assert (
        comparisons[1].mean_return_difference
        == pytest.approx(0.09)
    )


def test_accepts_empty_collections() -> None:
    assert BaselineComparator().compare(
        candidate=(),
        baseline=(),
    ) == ()


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("candidate", []),
        ("baseline", []),
    ),
)
def test_rejects_non_tuple_collection(
    field_name: str,
    invalid_value: object,
) -> None:
    arguments = {
        "candidate": (),
        "baseline": (),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a tuple",
    ):
        BaselineComparator().compare(
            **arguments
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "candidate",
        "baseline",
    ),
)
def test_rejects_invalid_statistics_item(
    field_name: str,
) -> None:
    arguments = {
        "candidate": (),
        "baseline": (),
    }
    arguments[field_name] = (object(),)

    with pytest.raises(
        TypeError,
        match=(
            f"each {field_name} value must be "
            "HorizonStatistics"
        ),
    ):
        BaselineComparator().compare(
            **arguments
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "candidate",
        "baseline",
    ),
)
def test_rejects_duplicate_horizons(
    field_name: str,
) -> None:
    duplicate_values = (
        build_statistics(1),
        build_statistics(1),
    )
    arguments = {
        "candidate": (),
        "baseline": (),
    }
    arguments[field_name] = duplicate_values

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must not contain "
            "duplicate horizons"
        ),
    ):
        BaselineComparator().compare(
            **arguments
        )


def test_rejects_different_horizon_sets(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate and baseline must contain "
            "the same horizons"
        ),
    ):
        BaselineComparator().compare(
            candidate=(
                build_statistics(1),
                build_statistics(5),
            ),
            baseline=(
                build_statistics(1),
                build_statistics(10),
            ),
        )
