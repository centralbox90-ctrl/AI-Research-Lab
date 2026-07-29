from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def generate_market_data(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    bars: int = 100,
    start_at: str | datetime = "2024-01-01T00:00:00Z",
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

    try:
        normalized_start = pd.Timestamp(
            start_at
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "start_at must be a valid timestamp"
        ) from error

    if pd.isna(normalized_start):
        raise ValueError(
            "start_at must be a valid timestamp"
        )

    if normalized_start.tzinfo is None:
        normalized_start = (
            normalized_start.tz_localize("UTC")
        )
    else:
        normalized_start = (
            normalized_start.tz_convert("UTC")
        )

    normalized_symbol = symbol.strip()
    normalized_timeframe = timeframe.strip()

    timestamps = pd.date_range(
        start=normalized_start,
        periods=bars,
        freq="h",
    )

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