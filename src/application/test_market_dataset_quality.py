from __future__ import annotations

import pandas as pd

from src.application.market_dataset_quality import (
    MarketDatasetQualityAnalyzer,
)

from src.application.market_dataset_fingerprint import (
    MarketDatasetCanonicalizer,
)

def create_canonical_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [
                100,
                200,
                300,
            ],
            "open": [
                1.0,
                2.0,
                3.0,
            ],
            "high": [
                1.5,
                2.5,
                3.5,
            ],
            "low": [
                0.5,
                1.5,
                2.5,
            ],
            "close": [
                1.2,
                2.2,
                3.2,
            ],
            "tick_volume": [
                10,
                20,
                30,
            ],
        }
    )


def test_quality_analyzer_returns_report():
    dataset = create_canonical_dataset()

    report = MarketDatasetQualityAnalyzer().analyze(
        dataset
    )

    assert report.row_count == 3
    assert report.first_timestamp == 100
    assert report.last_timestamp == 300
    assert report.duplicate_timestamp_count == 0
    assert report.missing_timestamp_count == 0
    assert report.invalid_ohlc_count == 0
    assert report.monotonic_timestamp is True


def test_quality_analyzer_detects_invalid_ohlc():
    dataset = create_canonical_dataset()

    dataset.loc[1, "high"] = 1.0
    dataset.loc[1, "low"] = 2.0

    report = MarketDatasetQualityAnalyzer().analyze(
        dataset
    )

    assert report.invalid_ohlc_count == 1


def test_quality_analyzer_rejects_empty_dataset():
    dataset = create_canonical_dataset().iloc[0:0]

    try:
        MarketDatasetQualityAnalyzer().analyze(
            dataset
        )
    except ValueError as error:
        assert (
            str(error)
            == "canonical market dataset cannot be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )
def test_quality_analyzer_accepts_canonical_dataset():

    raw = pd.DataFrame(
        {
            "timestamp": [
                "2025-01-01T00:00:00Z",
                "2025-01-01T01:00:00Z",
            ],
            "open": [
                1,
                2,
            ],
            "high": [
                2,
                3,
            ],
            "low": [
                0.5,
                1.5,
            ],
            "close": [
                1.5,
                2.5,
            ],
            "tick_volume": [
                100,
                200,
            ],
        }
    )

    canonical = MarketDatasetCanonicalizer().canonicalize(
        raw
    )

    report = MarketDatasetQualityAnalyzer().analyze(
        canonical
    )

    assert report.row_count == 2
    assert report.monotonic_timestamp is True
    assert report.invalid_ohlc_count == 0