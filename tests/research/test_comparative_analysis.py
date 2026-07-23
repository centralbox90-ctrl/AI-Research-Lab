from dataclasses import FrozenInstanceError

import pytest

from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_result(
    observation_ids: tuple[str, ...],
    *,
    horizon: int = 1,
) -> EventStudyResult:
    return EventStudyResult(
        specification=(
            ForwardReturnSpecification(
                horizons=(horizon,),
            )
        ),
        observation_ids=observation_ids,
        outcomes=tuple(
            ForwardReturnOutcome(
                observation_id=observation_id,
                horizon=horizon,
                start_bar_index=index,
                start_price=100.0,
                end_price=110.0,
            )
            for index, observation_id in enumerate(
                observation_ids
            )
        ),
    )


def build_statistics(
    horizon: int,
    sample_size: int,
) -> HorizonStatistics:
    return HorizonStatistics(
        horizon=horizon,
        sample_size=sample_size,
        mean_return=0.1,
        median_return=0.1,
        positive_rate=1.0,
        minimum_return=0.1,
        maximum_return=0.1,
    )


def build_comparison(
    horizon: int = 1,
    *,
    candidate_sample_size: int = 1,
    baseline_sample_size: int = 2,
) -> HorizonComparison:
    return HorizonComparison(
        horizon=horizon,
        candidate_sample_size=(
            candidate_sample_size
        ),
        baseline_sample_size=(
            baseline_sample_size
        ),
        mean_return_difference=0.0,
        median_return_difference=0.0,
        positive_rate_difference=0.0,
    )


def build_analysis(
    **changes: object,
) -> ComparativeAnalysis:
    values = {
        "candidate_result": build_result(
            ("candidate",)
        ),
        "baseline_result": build_result(
            (
                "baseline:0",
                "baseline:1",
            )
        ),
        "candidate_statistics": (
            build_statistics(1, 1),
        ),
        "baseline_statistics": (
            build_statistics(1, 2),
        ),
        "comparisons": (
            build_comparison(),
        ),
    }
    values.update(changes)

    return ComparativeAnalysis(**values)


def test_stores_consistent_analysis() -> None:
    analysis = build_analysis()

    assert (
        analysis.candidate_result
        .observation_count
        == 1
    )
    assert (
        analysis.baseline_result
        .observation_count
        == 2
    )
    assert analysis.comparisons[0].horizon == 1


def test_is_immutable() -> None:
    analysis = build_analysis()

    with pytest.raises(FrozenInstanceError):
        analysis.comparisons = ()


@pytest.mark.parametrize(
    ("field_name", "message"),
    (
        (
            "candidate_result",
            (
                "candidate_result must be an "
                "EventStudyResult"
            ),
        ),
        (
            "baseline_result",
            (
                "baseline_result must be an "
                "EventStudyResult"
            ),
        ),
    ),
)
def test_rejects_invalid_results(
    field_name: str,
    message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=message,
    ):
        build_analysis(
            **{field_name: object()}
        )


def test_rejects_different_specifications(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate and baseline must use "
            "the same specification"
        ),
    ):
        build_analysis(
            baseline_result=build_result(
                ("baseline",),
                horizon=5,
            )
        )


@pytest.mark.parametrize(
    ("field_name", "expected_type"),
    (
        (
            "candidate_statistics",
            "HorizonStatistics",
        ),
        (
            "baseline_statistics",
            "HorizonStatistics",
        ),
        (
            "comparisons",
            "HorizonComparison",
        ),
    ),
)
def test_rejects_invalid_collection_item(
    field_name: str,
    expected_type: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"each {field_name} value must be "
            f"{expected_type}"
        ),
    ):
        build_analysis(
            **{field_name: (object(),)}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "candidate_statistics",
        "baseline_statistics",
        "comparisons",
    ),
)
def test_rejects_non_tuple_collections(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a tuple",
    ):
        build_analysis(
            **{field_name: []}
        )


def test_rejects_missing_candidate_horizon(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate_statistics must cover "
            "all requested horizons"
        ),
    ):
        build_analysis(
            candidate_statistics=()
        )


def test_rejects_candidate_sample_size_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate sample size must match "
            "candidate observation count"
        ),
    ):
        build_analysis(
            candidate_statistics=(
                build_statistics(1, 2),
            )
        )


def test_rejects_baseline_sample_size_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "baseline sample size must match "
            "baseline observation count"
        ),
    ):
        build_analysis(
            baseline_statistics=(
                build_statistics(1, 1),
            )
        )


def test_rejects_comparison_sample_size_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "comparison sample sizes must match "
            "the analyzed statistics"
        ),
    ):
        build_analysis(
            comparisons=(
                build_comparison(
                    baseline_sample_size=3,
                ),
            )
        )
