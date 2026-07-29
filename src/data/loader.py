from __future__ import annotations

from datetime import datetime
import re

import numpy as np
import pandas as pd


def generate_market_data(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    bars: int = 100,
    start_at: str | datetime = "2024-01-01T00:00:00Z",
    end_at: str | datetime | None = None,
    random_seed: int = 0,
) -> pd.DataFrame:
    """Generate deterministic development market data."""

    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError(
            "symbol must be a non-empty string"
        )

    if (
        not isinstance(timeframe, str)
        or not timeframe.strip()
    ):
        raise ValueError(
            "timeframe must be a non-empty string"
        )

    if (
        not isinstance(bars, int)
        or isinstance(bars, bool)
        or bars < 1
    ):
        raise ValueError(
            "bars must be a positive integer"
        )

    if (
        not isinstance(random_seed, int)
        or isinstance(random_seed, bool)
        or random_seed < 0
    ):
        raise ValueError(
            "random_seed must be a "
            "non-negative integer"
        )

    normalized_start = _normalize_timestamp(
        start_at,
        field_name="start_at",
    )
    normalized_symbol = symbol.strip()
    normalized_timeframe = timeframe.strip()
    frequency = _normalize_timeframe_frequency(
        normalized_timeframe
    )

    if end_at is None:
        timestamps = pd.date_range(
            start=normalized_start,
            periods=bars,
            freq=frequency,
        )
    else:
        normalized_end = _normalize_timestamp(
            end_at,
            field_name="end_at",
        )

        if normalized_start >= normalized_end:
            raise ValueError(
                "start_at must be earlier than end_at"
            )

        timestamps = pd.date_range(
            start=normalized_start,
            end=normalized_end,
            freq=frequency,
            inclusive="left",
        )

        if timestamps.empty:
            raise ValueError(
                "declared period must contain at "
                "least one bar"
            )

        bars = len(timestamps)
    random = np.random.default_rng(random_seed)

    close = (
        100.0
        + random.standard_normal(bars).cumsum()
    )
    open_price = (
        close
        + random.normal(
            loc=0.0,
            scale=0.25,
            size=bars,
        )
    )
    high = (
        np.maximum(
            open_price,
            close,
        )
        + np.abs(
            random.normal(
                loc=0.0,
                scale=0.5,
                size=bars,
            )
        )
    )
    low = (
        np.minimum(
            open_price,
            close,
        )
        - np.abs(
            random.normal(
                loc=0.0,
                scale=0.5,
                size=bars,
            )
        )
    )

    return pd.DataFrame(
        {
            "symbol": normalized_symbol,
            "timeframe": normalized_timeframe,
            "bar_id": [
                (
                    f"{normalized_symbol}|"
                    f"{normalized_timeframe}|"
                    f"{timestamp.isoformat()}"
                )
                for timestamp in timestamps
            ],
            "Open": open_price,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": random.integers(
                low=1_000,
                high=10_000,
                size=bars,
            ),
        },
        index=timestamps,
    )

def _normalize_timestamp(
    value: str | datetime,
    *,
    field_name: str,
) -> pd.Timestamp:
    try:
        normalized = pd.Timestamp(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} must be a valid timestamp"
        ) from error

    if pd.isna(normalized):
        raise ValueError(
            f"{field_name} must be a valid timestamp"
        )

    if normalized.tzinfo is None:
        return normalized.tz_localize("UTC")

    return normalized.tz_convert("UTC")


def _normalize_timeframe_frequency(
    timeframe: str,
) -> str:
    normalized = timeframe.strip().upper()
    match = re.fullmatch(
        r"(?:(\d+)([MHD])|([MHD])(\d+))",
        normalized,
    )

    if match is None:
        raise ValueError(
            "timeframe must use forms such as "
            "H1, 1h, M15 or 1D"
        )

    amount_text = (
        match.group(1)
        or match.group(4)
    )
    unit_text = (
        match.group(2)
        or match.group(3)
    )
    amount = int(amount_text)

    if amount < 1:
        raise ValueError(
            "timeframe amount must be positive"
        )

    pandas_unit = {
        "M": "min",
        "H": "h",
        "D": "D",
    }[unit_text]

    return f"{amount}{pandas_unit}"
