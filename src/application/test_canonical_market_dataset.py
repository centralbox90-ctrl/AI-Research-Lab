from __future__ import annotations

import pandas as pd

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)

from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)

from src.application.market_dataset_quality import (
    DataQualityReport,
)


def test_canonical_market_dataset_contains_dataset_identity():

    data = pd.DataFrame(
        {
            "timestamp": [
                100,
            ],
            "open": [
                1.0,
            ],
            "high": [
                2.0,
            ],
            "low": [
                0.5,
            ],
            "close": [
                1.5,
            ],
            "tick_volume": [
                100,
            ],
        }
    )

    fingerprint = MarketDatasetFingerprint(
        content_fingerprint="content",
        dataset_fingerprint="dataset",
        algorithm="sha256",
        content_schema_version="v1",
        dataset_schema_version="v1",
        normalization_schema_version="v1",
    )

    quality = DataQualityReport(
        row_count=1,
        first_timestamp=100,
        last_timestamp=100,
        duplicate_timestamp_count=0,
        missing_timestamp_count=0,
        invalid_ohlc_count=0,
        monotonic_timestamp=True,
    )

    dataset = CanonicalMarketDataset(
        data=data,
        fingerprint=fingerprint,
        quality_report=quality,
    )

    assert dataset.data.equals(data)
    assert (
        dataset.fingerprint.dataset_fingerprint
        == "dataset"
    )
    assert dataset.quality_report.row_count == 1