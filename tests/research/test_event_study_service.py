from datetime import UTC, datetime

import pandas as pd
import pytest

from src.research.event_study_service import (
    EventStudyService,
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
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
                106.0,
            ],
        }
    )


def build_observation(
    observation_id: str,
    bar_index: int,
) -> Observation:
    return Observation(
        id=observation_id,
        definition_id="definition",
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
        horizons=(1, 2),
    )


def test_calculates_complete_observations_and_marks_incomplete(
) -> None:
    result = EventStudyService().run(
        data=build_data(),
        observations=(
            build_observation("complete", 1),
            build_observation("incomplete", 5),
        ),
        specification=build_specification(),
    )

    assert result.observation_ids == (
        "complete",
    )
    assert result.incomplete_observation_ids == (
        "incomplete",
    )
    assert tuple(
        outcome.horizon
        for outcome in result.outcomes
    ) == (1, 2)
    assert tuple(
        outcome.end_bar_index
        for outcome in result.outcomes
    ) == (2, 3)


def test_preserves_observation_order() -> None:
    result = EventStudyService().run(
        data=build_data(),
        observations=(
            build_observation("second", 2),
            build_observation("first", 0),
        ),
        specification=build_specification(),
    )

    assert result.observation_ids == (
        "second",
        "first",
    )
    assert tuple(
        outcome.observation_id
        for outcome in result.outcomes
    ) == (
        "second",
        "second",
        "first",
        "first",
    )


def test_accepts_empty_observation_collection(
) -> None:
    result = EventStudyService().run(
        data=build_data(),
        observations=(),
        specification=build_specification(),
    )

    assert result.observation_ids == ()
    assert result.outcomes == ()
    assert result.incomplete_observation_ids == ()


def test_does_not_modify_data() -> None:
    data = build_data()
    original = data.copy(deep=True)

    EventStudyService().run(
        data=data,
        observations=(
            build_observation("observation", 1),
        ),
        specification=build_specification(),
    )

    pd.testing.assert_frame_equal(
        data,
        original,
    )


@pytest.mark.parametrize(
    ("argument_name", "invalid_value", "message"),
    (
        (
            "data",
            object(),
            "data must be a pandas DataFrame",
        ),
        (
            "observations",
            [],
            "observations must be a tuple",
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
    argument_name: str,
    invalid_value: object,
    message: str,
) -> None:
    arguments = {
        "data": build_data(),
        "observations": (),
        "specification": build_specification(),
    }
    arguments[argument_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        EventStudyService().run(**arguments)


def test_rejects_invalid_observation_item(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each observation must be an "
            "Observation"
        ),
    ):
        EventStudyService().run(
            data=build_data(),
            observations=(object(),),
            specification=build_specification(),
        )


def test_rejects_duplicate_observation_ids(
) -> None:
    with pytest.raises(
        ValueError,
        match="observations must have unique ids",
    ):
        EventStudyService().run(
            data=build_data(),
            observations=(
                build_observation("duplicate", 0),
                build_observation("duplicate", 1),
            ),
            specification=build_specification(),
        )


def test_rejects_empty_data() -> None:
    with pytest.raises(
        ValueError,
        match="data must not be empty",
    ):
        EventStudyService().run(
            data=pd.DataFrame(
                {"close": []}
            ),
            observations=(),
            specification=build_specification(),
        )


def test_rejects_missing_price_field() -> None:
    with pytest.raises(
        ValueError,
        match="data is missing price field 'close'",
    ):
        EventStudyService().run(
            data=pd.DataFrame(
                {"open": [100.0]}
            ),
            observations=(),
            specification=build_specification(),
        )


def test_rejects_observation_outside_data(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "observation bar_index is outside data"
        ),
    ):
        EventStudyService().run(
            data=build_data(),
            observations=(
                build_observation("outside", 7),
            ),
            specification=build_specification(),
        )
