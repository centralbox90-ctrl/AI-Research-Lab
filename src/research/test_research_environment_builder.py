from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.research.research_environment_builder import (
    MissingDatasetFingerprintError,
    ResearchEnvironmentBuilder,
    StaleDatasetFingerprintError,
    UnsupportedFingerprintSchemaError,
)


def build_raw_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [
                datetime(
                    2024,
                    1,
                    1,
                    0,
                    tzinfo=timezone.utc,
                ),
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
                    2,
                    tzinfo=timezone.utc,
                ),
            ],
            "open": [1.0, 1.1, 1.2],
            "high": [1.1, 1.2, 1.3],
            "low": [0.9, 1.0, 1.1],
            "close": [1.05, 1.15, 1.25],
            "tick_volume": [100, 110, 120],
        }
    )


def build_fingerprinted_dataset() -> pd.DataFrame:
    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(build_raw_dataset())
    )

    MarketDatasetFingerprinter().attach(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    return canonical


def build_environment(
    data: pd.DataFrame,
):
    return ResearchEnvironmentBuilder().build(
        data,
        assumption_set_fingerprint="assumptions:001",
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )


def test_builder_creates_research_environment() -> None:
    data = build_fingerprinted_dataset()

    environment = build_environment(data)

    assert (
        environment.dataset_fingerprint
        == data.attrs["dataset_fingerprint"]
    )
    assert (
        environment.assumption_set_fingerprint
        == "assumptions:001"
    )


def test_builder_rejects_missing_fingerprint_metadata() -> None:
    data = (
        MarketDatasetCanonicalizer()
        .canonicalize(build_raw_dataset())
    )

    with pytest.raises(
        MissingDatasetFingerprintError,
        match="Canonical dataset has no fingerprint metadata",
    ):
        build_environment(data)


def test_builder_detects_stale_fingerprint_after_slicing() -> None:
    data = build_fingerprinted_dataset()

    subset = data.iloc[:2].copy()

    # Simulate pandas preserving or manually transferring attrs
    # after the dataset content has changed.
    subset.attrs.update(data.attrs)

    with pytest.raises(
        StaleDatasetFingerprintError,
        match="does not match",
    ):
        build_environment(subset)


def test_builder_rejects_unknown_schema_version() -> None:
    data = build_fingerprinted_dataset()

    data.attrs[
        "dataset_fingerprint_schema_version"
    ] = "market-dataset-fingerprint-v999"

    with pytest.raises(
        UnsupportedFingerprintSchemaError,
        match="Unsupported dataset fingerprint schema",
    ):
        build_environment(data)