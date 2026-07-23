from types import SimpleNamespace

import pytest

from src.application.indicator_research_result import (
    IndicatorResearchResult,
)


def build_result(
    *,
    series: object = (10.0, 20.0, 30.0),
    observations: object = (1, 0, -1),
    signals: tuple[object, ...] = (
        object(),
        object(),
        object(),
    ),
) -> IndicatorResearchResult:
    return IndicatorResearchResult(
        research_specification=object(),
        series=series,
        observations=observations,
        signal_result=SimpleNamespace(
            signals=signals,
        ),
    )


def test_stores_observations() -> None:
    result = build_result()

    assert result.observations == (
        1,
        0,
        -1,
    )


def test_rejects_non_tuple_observations() -> None:
    with pytest.raises(
        TypeError,
        match="observations must be a tuple",
    ):
        build_result(
            observations=[1, 0, -1]
        )


@pytest.mark.parametrize(
    "invalid_observation",
    (
        True,
        2,
        -2,
        0.5,
        "1",
    ),
)
def test_rejects_invalid_observation_value(
    invalid_observation: object,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "observations must contain only "
            "-1, 0, or 1"
        ),
    ):
        build_result(
            observations=(
                invalid_observation,
                0,
                0,
            )
        )


def test_rejects_series_observation_length_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "series and observations must have "
            "equal length"
        ),
    ):
        build_result(
            observations=(1, 0)
        )


def test_rejects_observation_signal_length_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "observations and signals must have "
            "equal length"
        ),
    ):
        build_result(
            signals=(
                object(),
                object(),
            )
        )
