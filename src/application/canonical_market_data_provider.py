from __future__ import annotations

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.legacy_market_data_frame_adapter import (
    LegacyMarketDataFrameAdapter,
)
from src.research.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)

from src.application.market_dataset_quality import (
    MarketDatasetQualityAnalyzer,
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
         legacy_adapter: LegacyMarketDataFrameAdapter | None = None,
         canonicalizer: MarketDatasetCanonicalizer | None = None,
         fingerprinter: MarketDatasetFingerprinter | None = None,
        quality_analyzer: MarketDatasetQualityAnalyzer | None = None,
    ) -> None:
        self._provider = provider
        self._legacy_adapter = (
            legacy_adapter
            or LegacyMarketDataFrameAdapter()
        )
        self._canonicalizer = (
            canonicalizer
            or MarketDatasetCanonicalizer()
        )
        self._fingerprinter = (
            fingerprinter
            or MarketDatasetFingerprinter()
        )
        self._quality_analyzer = (
            quality_analyzer
            or MarketDatasetQualityAnalyzer()
        )

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> CanonicalMarketDataset:
        source_data = self._provider.load(specification)

        canonical_input = self._legacy_adapter.adapt(
            source_data
        )

        canonical = self._canonicalizer.canonicalize(
            canonical_input
        )

        fingerprint = self._fingerprinter.attach(
            canonical,
            DatasetFingerprintContext(
                symbol=specification.symbol,
                timeframe=specification.timeframe,
                closed_bars_policy=(
                     "closed-bars-only-v1"
                ),
            ),
        )
        quality_report = (
           self._quality_analyzer.analyze(
                canonical
           )
        )

        dataset = CanonicalMarketDataset(
           data=canonical,
           fingerprint=fingerprint,
           quality_report=quality_report,
        )
        provenance = source_data.attrs.get(
            "provenance"
        )

        if provenance is not None:
            canonical.attrs["provenance"] = provenance

        return dataset
