import pytest

from src.research.event_study_analyzer import (
    EventStudyAnalyzer,
)
from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_outcome(
    observation_id: str,
    horizon: int,
    end_price: float,
) -> ForwardReturnOutcome:
    return ForwardReturnOutcome(
        observation_id=observation_id,
        horizon=horizon,
        start_bar_index=0,
        start_price=100.0,
        end_price=end_price,
    )


def build_result() -> EventStudyResult:
    specification = ForwardReturnSpecification(
        horizons=(3, 1),
    )

    return EventStudyResult(
        specification=specification,
        observation_ids=(
            "first",
            "second",
        ),
        outcomes=(
            build_outcome("first", 1, 110.0),
            build_outcome("first", 3, 80.0),
            build_outcome("second", 1, 90.0),
            build_outcome("second", 3, 120.0),
        ),
        incomplete_observation_ids=(
            "incomplete",
        ),
    )


def test_calculates_statistics_for_each_horizon(
) -> None:
    statistics = EventStudyAnalyzer().analyze(
        build_result()
    )

    assert tuple(
        item.horizon
        for item in statistics
    ) == (1, 3)

    one_bar, three_bars = statistics

    assert one_bar.sample_size == 2
    assert one_bar.mean_return == pytest.approx(
        0.0
    )
    assert one_bar.median_return == pytest.approx(
        0.0
    )
    assert one_bar.positive_rate == pytest.approx(
        0.5
    )
    assert one_bar.minimum_return == pytest.approx(
        -0.1
    )
    assert one_bar.maximum_return == pytest.approx(
        0.1
    )

    assert three_bars.sample_size == 2
    assert three_bars.mean_return == pytest.approx(
        0.0
    )
    assert three_bars.median_return == pytest.approx(
        0.0
    )
    assert three_bars.positive_rate == pytest.approx(
        0.5
    )
    assert three_bars.minimum_return == pytest.approx(
        -0.2
    )
    assert three_bars.maximum_return == pytest.approx(
        0.2
    )


def test_zero_return_is_not_positive() -> None:
    specification = ForwardReturnSpecification(
        horizons=(1,),
    )
    result = EventStudyResult(
        specification=specification,
        observation_ids=(
            "zero",
            "positive",
        ),
        outcomes=(
            build_outcome("zero", 1, 100.0),
            build_outcome(
                "positive",
                1,
                110.0,
            ),
        ),
    )

    statistics = EventStudyAnalyzer().analyze(
        result
    )

    assert statistics[0].positive_rate == (
        pytest.approx(0.5)
    )


def test_accepts_empty_event_study() -> None:
    result = EventStudyResult(
        specification=(
            ForwardReturnSpecification(
                horizons=(1, 5),
            )
        ),
        observation_ids=(),
        outcomes=(),
        incomplete_observation_ids=(
            "incomplete",
        ),
    )

    assert EventStudyAnalyzer().analyze(
        result
    ) == ()


def test_does_not_depend_on_outcome_order(
) -> None:
    original = build_result()
    reordered = EventStudyResult(
        specification=original.specification,
        observation_ids=(
            "first",
            "second",
        ),
        outcomes=tuple(
            reversed(original.outcomes)
        ),
        incomplete_observation_ids=(
            "incomplete",
        ),
    )

    assert EventStudyAnalyzer().analyze(
        reordered
    ) == EventStudyAnalyzer().analyze(
        original
    )


@pytest.mark.parametrize(
    "invalid_result",
    (
        None,
        object(),
        (),
    ),
)
def test_rejects_invalid_result(
    invalid_result: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="result must be an EventStudyResult",
    ):
        EventStudyAnalyzer().analyze(
            invalid_result
        )
