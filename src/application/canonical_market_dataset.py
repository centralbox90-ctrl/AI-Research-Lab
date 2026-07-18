from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.application.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)

from src.application.market_dataset_quality import (
    DataQualityReport,
)


@dataclass(frozen=True)
class CanonicalMarketDataset:
    """
    Immutable descriptor of a canonical market dataset.

    Contains market data and its research identity.
    """

    data: pd.DataFrame

    fingerprint: MarketDatasetFingerprint

    quality_report: DataQualityReport