from datetime import UTC, datetime, timedelta

import pytest

from src.application.observations.discovery import (
    discover_observations,
)
from src.application.observations.implementations.level_cross import (
    OBSERVATION,
    calculate_level_cross,
)
from src.indicators.series import IndicatorSeries
from src.indicators.specification import (
    IndicatorSpecification,
)


def build_series(
    values: tuple[float | None, ...],
) -> IndicatorSeries:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return IndicatorSeries.create(
        specification=IndicatorSpecification(
            indicator_type="test",
            version=1,
            parameters={},
        ),
        timestamps=tuple(
            start + timedelta(hours=index)
            for index in range(len(values))
        ),
        values=values,
        warmup_bars=0,
    )


def test_exports_level_cross_observation() -> None:
    assert OBSERVATION.observation_type == "level_cross"
    assert OBSERVATION.calculator is calculate_level_cross


def test_discovers_level_cross_observation() -> None:
    observation_types = {
        descriptor.observation_type
        for descriptor in discover_observations()
    }

    assert "level_cross" in observation_types


def test_calculates_cross_above() -> None:
    result = calculate_level_cross(
        build_series((
            None,
            20.0,
            30.0,
            40.0,
            30.0,
        )),
        {
            "level": 30.0,
            "direction": "cross_above",
        },
    )

    assert result == (0, 0, 1, 0, 0)


def test_calculates_cross_below() -> None:
    result = calculate_level_cross(
        build_series((
            None,
            40.0,
            30.0,
            20.0,
            30.0,
        )),
        {
            "level": 30.0,
            "direction": "cross_below",
        },
    )

    assert result == (0, 0, -1, 0, 0)


def test_requires_level() -> None:
    with pytest.raises(
        ValueError,
        match="level parameter is required",
    ):
        calculate_level_cross(
            build_series((20.0, 30.0)),
            {"direction": "cross_above"},
        )


def test_rejects_unsupported_direction() -> None:
    with pytest.raises(
        ValueError,
        match="direction must be",
    ):
        calculate_level_cross(
            build_series((20.0, 30.0)),
            {
                "level": 30.0,
                "direction": "sideways",
            },
        )
