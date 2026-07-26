from __future__ import annotations

import pandas as pd


class LegacyMarketDataFrameAdapter:
    """
    Maps the current legacy OHLC DataFrame into canonicalizer input.

    This adapter is the only application component that knows the
    legacy Open, High, Low, Close, and Volume column names.
    """

    REQUIRED_COLUMNS = (
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    )

    def adapt(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "legacy market data must be a pandas DataFrame"
            )

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing:
            raise ValueError(
                "market data provider returned unsupported "
                "columns. Missing legacy columns: "
                + ", ".join(missing)
            )

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError(
                "market data provider must return a "
                "DatetimeIndex until the provider contract "
                "is migrated to canonical timestamps"
            )

        return pd.DataFrame(
            {
                "timestamp": data.index.to_numpy(copy=True),
                "open": data["Open"].to_numpy(copy=True),
                "high": data["High"].to_numpy(copy=True),
                "low": data["Low"].to_numpy(copy=True),
                "close": data["Close"].to_numpy(copy=True),
                "tick_volume": data["Volume"].to_numpy(
                    copy=True
                ),
            }
        )
