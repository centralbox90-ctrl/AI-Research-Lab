from datetime import datetime, timezone

import pandas as pd

from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)


def build_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [
                datetime(
                    2024,
                    1,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
                datetime(
                    2024,
                    1,
                    1,
                    0,
                    tzinfo=timezone.utc,
                ),
            ],
            "open": [1.1, 1.0],
            "high": [1.2, 1.1],
            "low": [1.0, 0.9],
            "close": [1.15, 1.05],
            "tick_volume": [200, 100],
        }
    )


def context() -> DatasetFingerprintContext:
    return DatasetFingerprintContext(
        symbol="EURUSD",
        timeframe="H1",
    )


def test_canonicalizer_sorts_rows() -> None:
    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(build_dataset())
    )

    assert canonical["timestamp"].is_monotonic_increasing


def test_content_fingerprint_is_deterministic() -> None:
    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(build_dataset())
    )

    fingerprinter = MarketDatasetFingerprinter()

    first = fingerprinter.calculate(
        canonical,
        context(),
    )

    second = fingerprinter.calculate(
        canonical,
        context(),
    )

    assert (
        first.content_fingerprint
        == second.content_fingerprint
    )

    assert (
        first.dataset_fingerprint
        == second.dataset_fingerprint
    )


def test_dataset_fingerprint_changes_with_context() -> None:
    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(build_dataset())
    )

    fingerprinter = MarketDatasetFingerprinter()

    first = fingerprinter.calculate(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    second = fingerprinter.calculate(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="M30",
        ),
    )

    assert (
        first.content_fingerprint
        == second.content_fingerprint
    )

    assert (
        first.dataset_fingerprint
        != second.dataset_fingerprint
    )