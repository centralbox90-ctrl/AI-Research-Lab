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


def test_observation_descriptor_contracts() -> None:
    descriptor = ObservationDescriptor(
        observation_type="  oversold  ",
        calculator=simple_observation,
    )

    assert descriptor.observation_type == "oversold"
    assert descriptor.calculator is simple_observation

    with pytest.raises(
        TypeError,
        match="observation_type must be a string",
    ):
        ObservationDescriptor(
            observation_type=123,
            calculator=simple_observation,
        )

    with pytest.raises(
        ValueError,
        match="observation_type must not be empty",
    ):
        ObservationDescriptor(
            observation_type="   ",
            calculator=simple_observation,
        )

    with pytest.raises(
        TypeError,
        match="calculator must be callable",
    ):
        ObservationDescriptor(
            observation_type="oversold",
            calculator=None,
        )


def test_calculate_normalizes_type_and_forwards_parameters() -> None:
    received: dict[str, object] = {}
    parameters = {
        "threshold": -80.0,
    }

    def calculator(
        series: IndicatorSeries,
        calculator_parameters: dict[str, object],
    ) -> tuple[int, ...]:
        received["series"] = series
        received["parameters"] = calculator_parameters
        return (1, 0, 0)

    series = build_series()
    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="oversold",
                calculator=calculator,
            ),
        )
    )

    result = service.calculate(
        series=series,
        observation_type="  oversold  ",
        parameters=parameters,
    )

    assert result == (1, 0, 0)
    assert received["series"] is series
    assert received["parameters"] is parameters


def test_calculate_rejects_invalid_inputs() -> None:
    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="oversold",
                calculator=simple_observation,
            ),
        )
    )

    with pytest.raises(
        TypeError,
        match="series must be an IndicatorSeries",
    ):
        service.calculate(
            series=object(),
            observation_type="oversold",
            parameters={},
        )

    with pytest.raises(
        TypeError,
        match="observation_type must be a string",
    ):
        service.calculate(
            series=build_series(),
            observation_type=123,
            parameters={},
        )

    with pytest.raises(
        ValueError,
        match="observation_type must not be empty",
    ):
        service.calculate(
            series=build_series(),
            observation_type="   ",
            parameters={},
        )


def test_calculate_rejects_result_with_wrong_length() -> None:
    def wrong_length(
        series: IndicatorSeries,
        parameters: dict[str, object],
    ) -> tuple[int, ...]:
        return (1, 0)

    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="wrong-length",
                calculator=wrong_length,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Observation result length must match "
            "indicator series length"
        ),
    ):
        service.calculate(
            series=build_series(),
            observation_type="wrong-length",
            parameters={},
        )


@pytest.mark.parametrize(
    "invalid_signal",
    [
        True,
        False,
        -2,
        2,
        1.0,
        "1",
        None,
    ],
)
def test_calculate_rejects_noncanonical_signals(
    invalid_signal: object,
) -> None:
    def invalid_calculator(
        series: IndicatorSeries,
        parameters: dict[str, object],
    ) -> tuple[object, ...]:
        return (
            invalid_signal,
            0,
            0,
        )

    service = ObservationCalculationService(
        (
            ObservationDescriptor(
                observation_type="invalid",
                calculator=invalid_calculator,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Observation signals must contain "
            "only -1, 0, or 1"
        ),
    ):
        service.calculate(
            series=build_series(),
            observation_type="invalid",
            parameters={},
        )

