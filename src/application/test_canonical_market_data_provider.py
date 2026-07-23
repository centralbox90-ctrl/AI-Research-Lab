from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.canonical_market_data_provider import (
    CanonicalMarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application import (
    MarketPositionDirection,
)


class StubMarketDataProvider:
    def __init__(
        self,
        data: pd.DataFrame,
    ) -> None:
        self._data = data

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        return self._data.copy()


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Can canonical data be loaded?",
        question_description=(
            "Test canonical market data provider."
        ),
        hypothesis_title="Canonical data can be provided",
        hypothesis_description=(
            "Provider output can be normalized and fingerprinted."
        ),
        expected_result=(
            "A canonical fingerprinted dataset is returned."
        ),
        experiment_title="Canonical provider experiment",
        experiment_description=(
            "Load market data through the canonical decorator."
        ),
        data_source="stub",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            1,
            2,
            tzinfo=timezone.utc,
        ),
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def build_legacy_dataset() -> pd.DataFrame:
    index = pd.DatetimeIndex(
        [
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
        ]
    )

    data = pd.DataFrame(
        {
            "Open": [1.1, 1.0],
            "High": [1.2, 1.1],
            "Low": [1.0, 0.9],
            "Close": [1.15, 1.05],
            "Volume": [200, 100],
        },
        index=index,
    )

    data.attrs["provenance"] = {
        "data_source": "stub",
        "retrieved_at_utc": (
            "2024-01-01T00:00:00+00:00"
        ),
    }

    return data


def test_provider_returns_canonical_fingerprinted_data() -> None:
    provider = CanonicalMarketDataProvider(
        StubMarketDataProvider(
            build_legacy_dataset()
        )
    )

    dataset = provider.load(
        build_specification()
    )
    data = dataset.data

    assert isinstance(
        dataset,
        CanonicalMarketDataset,
    )
    assert (
        dataset.fingerprint.dataset_fingerprint
        == data.attrs["dataset_fingerprint"]
    )

    assert list(data.columns) == [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
    ]

    assert data["timestamp"].is_monotonic_increasing
    assert tuple(
        pd.to_datetime(
            data["timestamp"],
            unit="ns",
            utc=True,
        )
    ) == (
        pd.Timestamp("2024-01-01T00:00:00Z"),
        pd.Timestamp("2024-01-01T01:00:00Z"),
    )

    assert data.attrs[
        "content_fingerprint"
    ].startswith(
        "sha256:market-bars-content:v1:"
    )

    assert data.attrs[
        "dataset_fingerprint"
    ].startswith(
        "sha256:market-dataset:v1:"
    )


def test_provider_preserves_provenance() -> None:
    provider = CanonicalMarketDataProvider(
        StubMarketDataProvider(
            build_legacy_dataset()
        )
    )

    dataset = provider.load(
        build_specification()
    )
    data = dataset.data

    assert data.attrs["provenance"] == {
        "data_source": "stub",
        "retrieved_at_utc": (
            "2024-01-01T00:00:00+00:00"
        ),
    }


def test_provider_rejects_missing_legacy_column() -> None:
    source = build_legacy_dataset().drop(
        columns=["Volume"]
    )

    provider = CanonicalMarketDataProvider(
        StubMarketDataProvider(source)
    )

    with pytest.raises(
        ValueError,
        match="Missing legacy columns: Volume",
    ):
        provider.load(
            build_specification()
        )


def test_provider_rejects_non_datetime_index() -> None:
    source = build_legacy_dataset().reset_index(
        drop=True
    )

    provider = CanonicalMarketDataProvider(
        StubMarketDataProvider(source)
    )

    with pytest.raises(
        ValueError,
        match="must return a DatetimeIndex",
    ):
        provider.load(
            build_specification()
        )
def test_provider_generates_quality_metadata() -> None:
    provider = CanonicalMarketDataProvider(
        StubMarketDataProvider(
            build_legacy_dataset()
        )
    )

    dataset = provider.load(
        build_specification()
    )
    data = dataset.data

    assert dataset.quality_report.row_count == 2
    assert dataset.quality_report.monotonic_timestamp

    assert len(data) == 2

    assert data.attrs[
        "dataset_fingerprint"
    ].startswith(
        "sha256:market-dataset:v1:"
    )

    assert data["timestamp"].is_monotonic_increasing