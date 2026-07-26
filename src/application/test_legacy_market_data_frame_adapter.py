from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application.legacy_market_data_frame_adapter import (
    LegacyMarketDataFrameAdapter,
)


def build_legacy_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [1.0, 1.1],
            "High": [1.2, 1.3],
            "Low": [0.9, 1.0],
            "Close": [1.1, 1.2],
            "Volume": [100, 200],
            "ignored": ["a", "b"],
        },
        index=pd.DatetimeIndex(
            [
                datetime(
                    2024,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
                datetime(
                    2024,
                    1,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
            ]
        ),
    )


def test_maps_legacy_columns_to_canonicalizer_input(
) -> None:
    source = build_legacy_data()

    mapped = LegacyMarketDataFrameAdapter().adapt(
        source
    )

    assert tuple(mapped.columns) == (
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
    )
    assert tuple(mapped["open"]) == (1.0, 1.1)
    assert tuple(mapped["tick_volume"]) == (100, 200)
    assert tuple(mapped["timestamp"]) == tuple(
        source.index
    )


def test_does_not_modify_source_data() -> None:
    source = build_legacy_data()
    original = source.copy(deep=True)

    LegacyMarketDataFrameAdapter().adapt(source)

    pd.testing.assert_frame_equal(source, original)


def test_rejects_missing_legacy_column() -> None:
    source = build_legacy_data().drop(
        columns=["Volume"]
    )

    with pytest.raises(
        ValueError,
        match="Missing legacy columns: Volume",
    ):
        LegacyMarketDataFrameAdapter().adapt(source)


def test_rejects_non_datetime_index() -> None:
    source = build_legacy_data().reset_index(
        drop=True
    )

    with pytest.raises(
        ValueError,
        match="must return a DatetimeIndex",
    ):
        LegacyMarketDataFrameAdapter().adapt(source)


def test_rejects_non_dataframe() -> None:
    with pytest.raises(
        TypeError,
        match="must be a pandas DataFrame",
    ):
        LegacyMarketDataFrameAdapter().adapt(object())
