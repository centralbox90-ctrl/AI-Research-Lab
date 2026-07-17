from __future__ import annotations

import pandas as pd

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)


class CanonicalMarketDataProvider:
    """
    Decorates any MarketDataProvider with canonicalization and
    fingerprinting.

    The wrapped provider remains responsible only for loading
    source-specific market data and provenance.
    """

    def __init__(
        self,
        provider: MarketDataProvider,
        canonicalizer: MarketDatasetCanonicalizer | None = None,
        fingerprinter: MarketDatasetFingerprinter | None = None,
    ) -> None:
        self._provider = provider
        self._canonicalizer = (
            canonicalizer
            or MarketDatasetCanonicalizer()
        )
        self._fingerprinter = (
            fingerprinter
            or MarketDatasetFingerprinter()
        )

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        source_data = self._provider.load(specification)

        canonical_input = self._map_source_data(
            source_data
        )

        canonical = self._canonicalizer.canonicalize(
            canonical_input
        )

        self._fingerprinter.attach(
            canonical,
            DatasetFingerprintContext(
                symbol=specification.symbol,
                timeframe=specification.timeframe,
                closed_bars_policy=(
                    "closed-bars-only-v1"
                ),
            ),
        )

        provenance = source_data.attrs.get(
            "provenance"
        )

        if provenance is not None:
            canonical.attrs["provenance"] = provenance

        return canonical

    def _map_source_data(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert the current legacy provider format into the
        canonicalizer input contract.

        Temporary compatibility mapping:

        DateTimeIndex -> timestamp
        Open -> open
        High -> high
        Low -> low
        Close -> close
        Volume -> tick_volume
        """

        required_legacy_columns = (
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        )

        missing = [
            column
            for column in required_legacy_columns
            if column not in data.columns
        ]

        if missing:
            raise ValueError(
                "market data provider returned unsupported "
                "columns. Missing legacy columns: "
                + ", ".join(missing)
            )

        if not isinstance(
            data.index,
            pd.DatetimeIndex,
        ):
            raise ValueError(
                "market data provider must return a "
                "DatetimeIndex until the provider contract "
                "is migrated to canonical timestamps"
            )

        return pd.DataFrame(
            {
                "timestamp": data.index,
                "open": data["Open"],
                "high": data["High"],
                "low": data["Low"],
                "close": data["Close"],
                "tick_volume": data["Volume"],
            }
        )