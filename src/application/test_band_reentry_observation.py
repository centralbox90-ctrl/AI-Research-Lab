from datetime import UTC, datetime, timedelta

import pytest

from src.application.observations.discovery import (
    discover_observations,
)
from src.application.observations.implementations.band_reentry import (
    OBSERVATION,
    calculate_band_reentry,
)
from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification


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


def test_exports_and_discovers_band_reentry() -> None:
    assert OBSERVATION.observation_type == "band_reentry"
    assert OBSERVATION.calculator is calculate_band_reentry
    assert "band_reentry" in {
        descriptor.observation_type
        for descriptor in discover_observations()
    }


def test_calculates_both_band_reentries() -> None:
    result = calculate_band_reentry(
        build_series((
            None,
            -75.0,
            -70.0,
            -20.0,
            -31.0,
            -35.0,
        )),
        {
            "lower_level": -70.0,
            "upper_level": -30.0,
        },
    )

    assert result == (0, 0, 1, 0, -1, 0)


def test_rejects_overlapping_or_reversed_bands() -> None:
    with pytest.raises(
        ValueError,
        match="lower_level must be less than upper_level",
    ):
        calculate_band_reentry(
            build_series((-50.0, -40.0)),
            {
                "lower_level": -20.0,
                "upper_level": -30.0,
            },
        )
