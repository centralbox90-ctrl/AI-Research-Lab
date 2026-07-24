from __future__ import annotations

import numpy as np
import pandas as pd


def generate_market_data(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    bars: int = 100,
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

    normalized_symbol = symbol.strip()
    normalized_timeframe = timeframe.strip()

    timestamps = pd.date_range(
        start="2024-01-01T00:00:00Z",
        periods=bars,
        freq="h",
    )

    random = np.random.default_rng(0)

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