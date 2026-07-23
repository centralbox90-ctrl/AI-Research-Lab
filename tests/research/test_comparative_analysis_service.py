from datetime import UTC, datetime

import pandas as pd
import pytest

from src.research.comparative_analysis_service import (
    ComparativeAnalysisService,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "close": [
                100.0,
                110.0,
                120.0,
                130.0,
                140.0,
            ],
        }
    )


def build_observation(
    observation_id: str,
    bar_index: int,
) -> Observation:
    return Observation(
        id=observation_id,
        definition_id="williams-r-oversold",
        symbol="EURUSD",
        timeframe="H1",
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        bar_index=bar_index,
        price=100.0,
    )


def build_specification(
) -> ForwardReturnSpecification:
    return ForwardReturnSpecification(
        horizons=(2, 1),
    )


def test_runs_complete_comparative_analysis(
) -> None:
    analysis = ComparativeAnalysisService().run(
        data=build_data(),
        observations=(
            build_observation("candidate", 0),
        ),
        specification=build_specification(),
    )

    assert (
        analysis.candidate_result
        .observation_ids
        == ("candidate",)
    )
    assert (
        analysis.baseline_result
        .observation_ids
        == (
            "baseline:0",
            "baseline:1",
            "baseline:2",
        )
    )

    assert tuple(
        statistics.horizon
        for statistics in (
            analysis.candidate_statistics
        )
    ) == (1, 2)
    assert tuple(
        statistics.sample_size
        for statistics in (
            analysis.candidate_statistics
        )
    ) == (1, 1)
    assert tuple(
        statistics.sample_size
        for statistics in (
            analysis.baseline_statistics
        )
    ) == (3, 3)
    assert tuple(
        comparison.horizon
        for comparison in analysis.comparisons
    ) == (1, 2)


def test_comparison_matches_analyzed_statistics(
) -> None:
    analysis = ComparativeAnalysisService().run(
        data=build_data(),
        observations=(
            build_observation("candidate", 0),
        ),
        specification=build_specification(),
    )

    for (
        candidate,
        baseline,
        comparison,
    ) in zip(
        analysis.candidate_statistics,
        analysis.baseline_statistics,
        analysis.comparisons,
        strict=True,
    ):
        assert (
            comparison.mean_return_difference
            == pytest.approx(
                candidate.mean_return
                - baseline.mean_return
            )
        )
        assert (
            comparison.median_return_difference
            == pytest.approx(
                candidate.median_return
                - baseline.median_return
            )
        )
        assert (
            comparison.positive_rate_difference
            == pytest.approx(
                candidate.positive_rate
                - baseline.positive_rate
            )
        )


def test_preserves_incomplete_candidate_observations(
) -> None:
    analysis = ComparativeAnalysisService().run(
        data=build_data(),
        observations=(
            build_observation("complete", 0),
            build_observation("incomplete", 3),
        ),
        specification=build_specification(),
    )

    assert (
        analysis.candidate_result
        .observation_ids
        == ("complete",)
    )
    assert (
        analysis.candidate_result
        .incomplete_observation_ids
        == ("incomplete",)
    )


def test_rejects_study_without_complete_observations(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate event study contains no "
            "complete observations"
        ),
    ):
        ComparativeAnalysisService().run(
            data=build_data(),
            observations=(
                build_observation(
                    "incomplete",
                    3,
                ),
            ),
            specification=build_specification(),
        )


def test_rejects_empty_observation_collection(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate event study contains no "
            "complete observations"
        ),
    ):
        ComparativeAnalysisService().run(
            data=build_data(),
            observations=(),
            specification=build_specification(),
        )


def test_delegates_input_validation() -> None:
    with pytest.raises(
        TypeError,
        match="data must be a pandas DataFrame",
    ):
        ComparativeAnalysisService().run(
            data=object(),
            observations=(),
            specification=build_specification(),
        )


def test_does_not_modify_data() -> None:
    data = build_data()
    original = data.copy(deep=True)

    ComparativeAnalysisService().run(
        data=data,
        observations=(
            build_observation("candidate", 0),
        ),
        specification=build_specification(),
    )

    pd.testing.assert_frame_equal(
        data,
        original,
    )
