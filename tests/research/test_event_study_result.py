from dataclasses import FrozenInstanceError

import pytest

from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_specification() -> ForwardReturnSpecification:
    return ForwardReturnSpecification(
        horizons=(1, 5),
    )


def build_outcome(
    *,
    observation_id: str,
    horizon: int,
) -> ForwardReturnOutcome:
    return ForwardReturnOutcome(
        observation_id=observation_id,
        horizon=horizon,
        start_bar_index=10,
        start_price=100.0,
        end_price=105.0,
    )


def build_complete_outcomes() -> tuple[
    ForwardReturnOutcome,
    ...,
]:
    return (
        build_outcome(
            observation_id="observation-1",
            horizon=1,
        ),
        build_outcome(
            observation_id="observation-1",
            horizon=5,
        ),
        build_outcome(
            observation_id="observation-2",
            horizon=1,
        ),
        build_outcome(
            observation_id="observation-2",
            horizon=5,
        ),
    )


def test_stores_complete_and_incomplete_observations() -> None:
    result = EventStudyResult(
        specification=build_specification(),
        observation_ids=(
            "observation-1",
            "observation-2",
        ),
        outcomes=build_complete_outcomes(),
        incomplete_observation_ids=(
            "observation-3",
        ),
    )

    assert result.observation_count == 2
    assert result.incomplete_observation_count == 1
    assert result.outcome_count == 4
    assert result.incomplete_observation_ids == (
        "observation-3",
    )


def test_normalizes_observation_ids() -> None:
    result = EventStudyResult(
        specification=ForwardReturnSpecification(
            horizons=(1,),
        ),
        observation_ids=(
            "  observation-1  ",
        ),
        outcomes=(
            build_outcome(
                observation_id="observation-1",
                horizon=1,
            ),
        ),
        incomplete_observation_ids=(
            "  observation-2  ",
        ),
    )

    assert result.observation_ids == (
        "observation-1",
    )
    assert result.incomplete_observation_ids == (
        "observation-2",
    )


def test_accepts_empty_event_study() -> None:
    result = EventStudyResult(
        specification=build_specification(),
        observation_ids=(),
        outcomes=(),
    )

    assert result.observation_count == 0
    assert result.outcome_count == 0


@pytest.mark.parametrize(
    "field_name",
    [
        "observation_ids",
        "incomplete_observation_ids",
    ],
)
def test_rejects_non_tuple_id_collections(
    field_name: str,
) -> None:
    arguments: dict[str, object] = {
        "specification": build_specification(),
        "observation_ids": (),
        "outcomes": (),
        "incomplete_observation_ids": (),
    }
    arguments[field_name] = []

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a tuple",
    ):
        EventStudyResult(**arguments)


@pytest.mark.parametrize(
    "field_name",
    [
        "observation_ids",
        "incomplete_observation_ids",
    ],
)
def test_rejects_duplicate_ids(
    field_name: str,
) -> None:
    arguments: dict[str, object] = {
        "specification": build_specification(),
        "observation_ids": (),
        "outcomes": (),
        "incomplete_observation_ids": (),
    }
    arguments[field_name] = (
        "duplicate",
        "duplicate",
    )

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not contain duplicates",
    ):
        EventStudyResult(**arguments)


def test_rejects_overlapping_complete_and_incomplete_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "complete and incomplete observation "
            "ids must be disjoint"
        ),
    ):
        EventStudyResult(
            specification=build_specification(),
            observation_ids=("observation-1",),
            outcomes=(
                build_outcome(
                    observation_id="observation-1",
                    horizon=1,
                ),
                build_outcome(
                    observation_id="observation-1",
                    horizon=5,
                ),
            ),
            incomplete_observation_ids=(
                "observation-1",
            ),
        )


def test_rejects_missing_requested_outcome() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "outcomes must cover every complete "
            "observation and requested horizon"
        ),
    ):
        EventStudyResult(
            specification=build_specification(),
            observation_ids=("observation-1",),
            outcomes=(
                build_outcome(
                    observation_id="observation-1",
                    horizon=1,
                ),
            ),
        )


def test_rejects_outcome_for_unknown_observation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "outcomes must cover every complete "
            "observation and requested horizon"
        ),
    ):
        EventStudyResult(
            specification=ForwardReturnSpecification(
                horizons=(1,),
            ),
            observation_ids=("observation-1",),
            outcomes=(
                build_outcome(
                    observation_id="observation-2",
                    horizon=1,
                ),
            ),
        )


def test_rejects_duplicate_outcome_pairs() -> None:
    outcome = build_outcome(
        observation_id="observation-1",
        horizon=1,
    )

    with pytest.raises(
        ValueError,
        match=(
            "outcomes must not contain duplicate "
            "observation and horizon pairs"
        ),
    ):
        EventStudyResult(
            specification=ForwardReturnSpecification(
                horizons=(1,),
            ),
            observation_ids=("observation-1",),
            outcomes=(
                outcome,
                outcome,
            ),
        )


def test_rejects_invalid_contract_types() -> None:
    with pytest.raises(
        TypeError,
        match="specification must be a",
    ):
        EventStudyResult(
            specification=object(),
            observation_ids=(),
            outcomes=(),
        )

    with pytest.raises(
        TypeError,
        match="outcomes must be a tuple",
    ):
        EventStudyResult(
            specification=build_specification(),
            observation_ids=(),
            outcomes=[],
        )

    with pytest.raises(
        TypeError,
        match="each outcome must be a",
    ):
        EventStudyResult(
            specification=build_specification(),
            observation_ids=(),
            outcomes=(object(),),
        )


def test_is_immutable() -> None:
    result = EventStudyResult(
        specification=build_specification(),
        observation_ids=(),
        outcomes=(),
    )

    with pytest.raises(FrozenInstanceError):
        result.outcomes = ()
