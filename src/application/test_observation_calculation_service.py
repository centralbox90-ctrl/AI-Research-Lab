from datetime import datetime, timezone

import pytest

from src.application.observation_calculation_service import (
    ObservationCalculationService,
    ObservationDescriptor,
)
from src.indicators.series import IndicatorSeries
from src.indicators.specification import (
    IndicatorSpecification,
)


def build_series() -> IndicatorSeries:
    return IndicatorSeries.create(
        specification=IndicatorSpecification(
            indicator_type="williams_r",
            version=1,
            parameters={},
        ),
        timestamps=(
            datetime(
                2024,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2024,
                1,
                2,
                tzinfo=timezone.utc,
            ),
            datetime(
                2024,
                1,
                3,
                tzinfo=timezone.utc,
            ),
        ),
        values=(
            -90.0,
            -75.0,
            -20.0,
        ),
        warmup_bars=0,
    )


def simple_observation(
    series: IndicatorSeries,
    parameters: dict[str, object],
) -> tuple[int, ...]:
    return tuple(
        1 if value is not None and value < -80 else 0
        for value in series.values
    )


def test_calculate_observation() -> None:
    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="oversold",
                calculator=simple_observation,
            ),
        ),
    )

    signals = service.calculate(
        series=build_series(),
        observation_type="oversold",
        parameters={},
    )

    assert signals == (
        1,
        0,
        0,
    )


def test_unknown_observation_type() -> None:
    service = ObservationCalculationService(())

    with pytest.raises(
        KeyError,
        match="Unknown observation type",
    ):
        service.calculate(
            series=build_series(),
            observation_type="missing",
            parameters={},
        )


def test_duplicate_registration() -> None:
    descriptor = ObservationDescriptor(
        observation_type="oversold",
        calculator=simple_observation,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate observation type",
    ):
        ObservationCalculationService(
            (
                descriptor,
                descriptor,
            ),
        )


def invalid_observation(
    series: IndicatorSeries,
    parameters: dict[str, object],
) -> tuple[int, ...]:
    return (
        5,
        5,
        5,
    )


def test_invalid_signal_values() -> None:
    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="invalid",
                calculator=invalid_observation,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="Observation signals",
    ):
        service.calculate(
            series=build_series(),
            observation_type="invalid",
            parameters={},
        )
