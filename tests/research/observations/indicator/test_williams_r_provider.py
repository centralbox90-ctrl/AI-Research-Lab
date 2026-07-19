from datetime import UTC, datetime, timedelta

import pytest

from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification
from src.research.observations.indicator.williams_r_definition import (
    WilliamsRObservationDefinition,
)
from src.research.observations.indicator.williams_r_provider import (
    WilliamsRObservationProvider,
)


def make_specification() -> IndicatorSpecification:
    return IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 3,
        },
    )


def make_definition(
    *,
    direction: str = "cross_above",
    level: float = -80.0,
) -> WilliamsRObservationDefinition:
    return WilliamsRObservationDefinition(
        id="definition-1",
        question_id="question-1",
        hypothesis_id="hypothesis-1",
        title="Williams crossing",
        description="Williams crosses a configured level",
        observation_type="indicator",
        indicator=make_specification(),
        level=level,
        direction=direction,
    )


def make_series(
    values: tuple[float | None, ...],
) -> IndicatorSeries:
    start = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    timestamps = tuple(
        start + timedelta(hours=index)
        for index in range(len(values))
    )

    return IndicatorSeries.create(
        specification=make_specification(),
        timestamps=timestamps,
        values=values,
        warmup_bars=2,
        metadata={
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    )


def test_detects_cross_above_level() -> None:
    provider = WilliamsRObservationProvider()

    observations = provider.observe(
        make_series(
            (
                None,
                -90.0,
                -80.0,
                -79.0,
                -70.0,
            )
        ),
        make_definition(),
    )

    assert len(observations) == 1

    observation = observations[0]

    assert observation.definition_id == "definition-1"
    assert observation.symbol == "BTCUSDT"
    assert observation.timeframe == "1h"
    assert observation.bar_index == 3
    assert observation.price is None
    assert observation.context["indicator_value"] == -79.0
    assert observation.context[
        "previous_indicator_value"
    ] == -80.0


def test_detects_cross_below_level() -> None:
    provider = WilliamsRObservationProvider()

    observations = provider.observe(
        make_series(
            (
                None,
                -10.0,
                -20.0,
                -21.0,
            )
        ),
        make_definition(
            direction="cross_below",
            level=-20.0,
        ),
    )

    assert len(observations) == 1
    assert observations[0].bar_index == 3


def test_does_not_emit_repeated_observation_above_level() -> None:
    provider = WilliamsRObservationProvider()

    observations = provider.observe(
        make_series(
            (
                -90.0,
                -79.0,
                -70.0,
                -60.0,
            )
        ),
        make_definition(),
    )

    assert len(observations) == 1


def test_ignores_warmup_values() -> None:
    provider = WilliamsRObservationProvider()

    observations = provider.observe(
        make_series(
            (
                None,
                None,
                -70.0,
            )
        ),
        make_definition(),
    )

    assert observations == []


def test_rejects_mismatched_series_specification() -> None:
    other_specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 14,
        },
    )

    series = IndicatorSeries.create(
        specification=other_specification,
        timestamps=(
            datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
            datetime(
                2026,
                1,
                2,
                tzinfo=UTC,
            ),
        ),
        values=(
            -90.0,
            -70.0,
        ),
        warmup_bars=1,
    )

    provider = WilliamsRObservationProvider()

    with pytest.raises(
        ValueError,
        match="series specification does not match",
    ):
        provider.observe(
            series,
            make_definition(),
        )


@pytest.mark.parametrize(
    "level",
    [
        -101.0,
        1.0,
    ],
)
def test_definition_rejects_invalid_level(
    level: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="level must be between -100 and 0",
    ):
        make_definition(
            level=level,
        )


def test_definition_rejects_incorrect_indicator() -> None:
    specification = IndicatorSpecification(
        indicator_type="rsi",
        version=1,
        parameters={
            "period": 14,
        },
    )

    with pytest.raises(
        ValueError,
        match="indicator_type='williams_r'",
    ):
        WilliamsRObservationDefinition(
            id="definition-1",
            question_id="question-1",
            hypothesis_id="hypothesis-1",
            title="Invalid definition",
            description="Invalid indicator type",
            observation_type="indicator",
            indicator=specification,
            level=-80.0,
            direction="cross_above",
        )