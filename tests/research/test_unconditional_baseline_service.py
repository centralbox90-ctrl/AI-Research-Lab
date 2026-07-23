import pandas as pd
import pytest

from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.unconditional_baseline_service import (
    UnconditionalBaselineService,
)


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "close": [
                100.0,
                110.0,
                121.0,
                133.1,
                146.41,
            ],
        }
    )


def build_specification(
) -> ForwardReturnSpecification:
    return ForwardReturnSpecification(
        horizons=(2, 1),
    )


def test_builds_outcomes_for_all_complete_points(
) -> None:
    result = (
        UnconditionalBaselineService().build(
            data=build_data(),
            specification=build_specification(),
        )
    )

    assert result.observation_ids == (
        "baseline:0",
        "baseline:1",
        "baseline:2",
    )
    assert result.incomplete_observation_ids == ()
    assert result.observation_count == 3
    assert result.outcome_count == 6

    assert tuple(
        (
            outcome.observation_id,
            outcome.horizon,
            outcome.start_bar_index,
            outcome.end_bar_index,
        )
        for outcome in result.outcomes
    ) == (
        ("baseline:0", 1, 0, 1),
        ("baseline:0", 2, 0, 2),
        ("baseline:1", 1, 1, 2),
        ("baseline:1", 2, 1, 3),
        ("baseline:2", 1, 2, 3),
        ("baseline:2", 2, 2, 4),
    )


def test_calculates_expected_returns() -> None:
    result = (
        UnconditionalBaselineService().build(
            data=build_data(),
            specification=build_specification(),
        )
    )

    assert tuple(
        outcome.value
        for outcome in result.outcomes
    ) == pytest.approx(
        (
            0.1,
            0.21,
            0.1,
            0.21,
            0.1,
            0.21,
        )
    )


def test_uses_configured_price_field() -> None:
    data = pd.DataFrame(
        {
            "open": [
                50.0,
                55.0,
                60.5,
            ],
            "close": [
                100.0,
                100.0,
                100.0,
            ],
        }
    )
    specification = ForwardReturnSpecification(
        horizons=(1,),
        price_field="open",
    )

    result = (
        UnconditionalBaselineService().build(
            data=data,
            specification=specification,
        )
    )

    assert tuple(
        outcome.value
        for outcome in result.outcomes
    ) == pytest.approx(
        (
            0.1,
            0.1,
        )
    )


def test_does_not_modify_data() -> None:
    data = build_data()
    original = data.copy(deep=True)

    UnconditionalBaselineService().build(
        data=data,
        specification=build_specification(),
    )

    pd.testing.assert_frame_equal(
        data,
        original,
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    (
        (
            "data",
            object(),
            "data must be a pandas DataFrame",
        ),
        (
            "specification",
            object(),
            (
                "specification must be a "
                "ForwardReturnSpecification"
            ),
        ),
    ),
)
def test_rejects_invalid_arguments(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    arguments = {
        "data": build_data(),
        "specification": build_specification(),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        UnconditionalBaselineService().build(
            **arguments
        )


def test_rejects_empty_data() -> None:
    with pytest.raises(
        ValueError,
        match="data must not be empty",
    ):
        UnconditionalBaselineService().build(
            data=pd.DataFrame(
                {"close": []}
            ),
            specification=build_specification(),
        )


def test_rejects_missing_price_field() -> None:
    with pytest.raises(
        ValueError,
        match="data is missing price field 'close'",
    ):
        UnconditionalBaselineService().build(
            data=pd.DataFrame(
                {"open": [100.0, 101.0, 102.0]}
            ),
            specification=build_specification(),
        )


def test_rejects_data_without_complete_point(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "data does not contain any complete "
            "baseline points"
        ),
    ):
        UnconditionalBaselineService().build(
            data=pd.DataFrame(
                {
                    "close": [
                        100.0,
                        101.0,
                    ],
                }
            ),
            specification=build_specification(),
        )


def test_includes_single_complete_point() -> None:
    result = (
        UnconditionalBaselineService().build(
            data=pd.DataFrame(
                {
                    "close": [
                        100.0,
                        110.0,
                        120.0,
                    ],
                }
            ),
            specification=build_specification(),
        )
    )

    assert result.observation_ids == (
        "baseline:0",
    )
    assert result.outcome_count == 2
