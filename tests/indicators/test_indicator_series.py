from datetime import UTC, datetime, timedelta

import pytest

from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification


def make_specification() -> IndicatorSpecification:
    return IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 3,
        },
    )


def make_timestamps(count: int) -> list[datetime]:
    start = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    return [
        start + timedelta(hours=index)
        for index in range(count)
    ]


def test_indicator_series_stores_reproducible_result() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(4),
        values=[
            None,
            None,
            -75.0,
            -60.0,
        ],
        warmup_bars=2,
        source_data_ref="dataset:eurusd-h1-v1",
        metadata={
            "implementation": "native",
        },
    )

    assert len(series) == 4
    assert series.valid_from == 2
    assert series.value_at(2) == -75.0
    assert series.timestamp_at(2) == make_timestamps(4)[2]
    assert series.source_data_ref == "dataset:eurusd-h1-v1"
    assert series.metadata["implementation"] == "native"


def test_indicator_series_rejects_different_lengths() -> None:
    with pytest.raises(
        ValueError,
        match="timestamps and values must have equal length",
    ):
        IndicatorSeries.create(
            specification=make_specification(),
            timestamps=make_timestamps(2),
            values=[
                None,
            ],
            warmup_bars=1,
        )


def test_indicator_series_rejects_negative_warmup() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "warmup_bars must be greater than or equal to zero"
        ),
    ):
        IndicatorSeries.create(
            specification=make_specification(),
            timestamps=make_timestamps(1),
            values=[
                None,
            ],
            warmup_bars=-1,
        )


def test_indicator_series_rejects_warmup_above_length() -> None:
    with pytest.raises(
        ValueError,
        match="warmup_bars must not exceed series length",
    ):
        IndicatorSeries.create(
            specification=make_specification(),
            timestamps=make_timestamps(1),
            values=[
                None,
            ],
            warmup_bars=2,
        )


def test_indicator_series_returns_none_without_valid_values() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(2),
        values=[
            None,
            None,
        ],
        warmup_bars=2,
    )

    assert series.valid_from is None


def test_indicator_series_copies_input_sequences() -> None:
    timestamps = make_timestamps(2)
    values: list[float | None] = [
        None,
        -70.0,
    ]

    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=timestamps,
        values=values,
        warmup_bars=1,
    )

    values[1] = -10.0

    assert series.values == (
        None,
        -70.0,
    )


def test_indicator_series_metadata_is_read_only() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(1),
        values=[
            -50.0,
        ],
        warmup_bars=0,
        metadata={
            "implementation": "native",
        },
    )

    with pytest.raises(TypeError):
        series.metadata["implementation"] = "changed"


def test_indicator_series_rejects_blank_source_reference() -> None:
    with pytest.raises(
        ValueError,
        match="source_data_ref must not be empty when provided",
    ):
        IndicatorSeries.create(
            specification=make_specification(),
            timestamps=make_timestamps(1),
            values=[
                -50.0,
            ],
            warmup_bars=0,
            source_data_ref=" ",
        )


def test_indicator_series_preserves_specification_identity() -> None:
    specification = make_specification()

    series = IndicatorSeries.create(
        specification=specification,
        timestamps=make_timestamps(3),
        values=[
            None,
            -75.0,
            -60.0,
        ],
        warmup_bars=1,
    )

    assert series.specification is specification

def test_indicator_series_create_preserves_specification_identity() -> None:
    specification = make_specification()

    series = IndicatorSeries.create(
        specification=specification,
        timestamps=make_timestamps(2),
        values=[
            None,
            -70.0,
        ],
        warmup_bars=1,
    )

    assert series.specification is specification

def test_indicator_series_normalizes_source_reference() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(1),
        values=[
            -50.0,
        ],
        warmup_bars=0,
        source_data_ref="  dataset:eurusd-h1-v1  ",
    )

    assert series.source_data_ref == "dataset:eurusd-h1-v1"

def test_indicator_series_copies_metadata() -> None:
    metadata = {
        "implementation": "native",
    }

    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(1),
        values=[
            -50.0,
        ],
        warmup_bars=0,
        metadata=metadata,
    )

    metadata["implementation"] = "modified"
    metadata["new_key"] = "value"

    assert series.metadata == {
        "implementation": "native",
    }

def test_indicator_series_defaults_to_empty_metadata() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(1),
        values=[
            -50.0,
        ],
        warmup_bars=0,
    )

    assert series.metadata == {}

    with pytest.raises(TypeError):
        series.metadata["key"] = "value"

def test_indicator_series_normalizes_sequences_to_tuples() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(2),
        values=[
            None,
            -70.0,
        ],
        warmup_bars=1,
    )

    assert isinstance(series.timestamps, tuple)
    assert isinstance(series.values, tuple)

def test_indicator_series_value_at_supports_negative_index() -> None:
    series = IndicatorSeries.create(
        specification=make_specification(),
        timestamps=make_timestamps(3),
        values=[
            None,
            -70.0,
            -55.0,
        ],
        warmup_bars=1,
    )

    assert series.value_at(-1) == -55.0
    assert series.value_at(-2) == -70.0

