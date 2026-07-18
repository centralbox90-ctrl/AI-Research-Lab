from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DataQualityReport:
    """
    Describes quality characteristics of a canonical market dataset.
    """

    row_count: int

    first_timestamp: int

    last_timestamp: int

    duplicate_timestamp_count: int

    missing_timestamp_count: int

    invalid_ohlc_count: int

    monotonic_timestamp: bool


class MarketDatasetQualityAnalyzer:
    """
    Analyzes canonical market datasets.

    This component does not modify data.
    It only produces a quality report.
    """

    def analyze(
        self,
        canonical_data: pd.DataFrame,
    ) -> DataQualityReport:

        if canonical_data.empty:
            raise ValueError(
                "canonical market dataset cannot be empty"
            )

        timestamps = canonical_data[
            "timestamp"
        ]

        duplicate_count = int(
            timestamps.duplicated(
                keep=False
            ).sum()
        )

        missing_timestamp_count = int(
            timestamps.isna().sum()
        )

        invalid_ohlc_count = int(
            (
                (canonical_data["high"] < canonical_data["low"])
                |
                (canonical_data["open"] <= 0)
                |
                (canonical_data["high"] <= 0)
                |
                (canonical_data["low"] <= 0)
                |
                (canonical_data["close"] <= 0)
            )
            .sum()
        )

        return DataQualityReport(
            row_count=len(canonical_data),

            first_timestamp=int(
                timestamps.iloc[0]
            ),

            last_timestamp=int(
                timestamps.iloc[-1]
            ),

            duplicate_timestamp_count=(
                duplicate_count
            ),

            missing_timestamp_count=(
                missing_timestamp_count
            ),

            invalid_ohlc_count=(
                invalid_ohlc_count
            ),

            monotonic_timestamp=(
                timestamps
                .is_monotonic_increasing
            ),
        )