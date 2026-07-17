from datetime import datetime, timezone

import pandas as pd

from src.application import (
    MarketDataProvider,
    MarketExperimentSpecification,
    MarketPositionDirection,
)


class MarketDataProviderImplementation:
    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Open": [100.0],
                "High": [101.0],
                "Low": [99.0],
                "Close": [100.5],
                "Volume": [1000.0],
            }
        )


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Can market data be loaded?",
        question_description=(
            "Test the market data provider application boundary."
        ),
        hypothesis_title="Market data can be provided",
        hypothesis_description=(
            "A registered provider can load market data for "
            "a validated specification."
        ),
        expected_result="A non-empty market data frame is returned.",
        experiment_title="Market data provider experiment",
        experiment_description=(
            "Load historical market data through the provider boundary."
        ),
        data_source="historical_csv",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def test_market_data_provider_defines_data_boundary() -> None:
    provider: MarketDataProvider = MarketDataProviderImplementation()

    specification = build_specification()
    data = provider.load(specification)

    assert list(data.columns) == [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]
    assert len(data) == 1
    assert data.iloc[0]["Close"] == 100.5