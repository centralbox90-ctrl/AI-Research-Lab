from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application.market_data_provider_router import (
    MarketDataProviderRouter,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)


class StubProvider:
    def __init__(self, value: float) -> None:
        self.value = value
        self.loaded = []

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        self.loaded.append(specification)

        return pd.DataFrame(
            {"Close": [self.value]}
        )


def build_specification(
    data_source: str,
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Can the source be routed?",
        question_description=(
            "Route one market data request."
        ),
        hypothesis_title=(
            "The registered source is used"
        ),
        hypothesis_description=(
            "Routing follows data_source."
        ),
        expected_result=(
            "The selected provider returns data."
        ),
        experiment_title=(
            "Market data routing test"
        ),
        experiment_description=(
            "Load data through the router."
        ),
        data_source=data_source,
        symbol="XAUUSD",
        timeframe="H1",
        start_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2026,
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="rsi < 30",
        exit_rule="rsi > 50",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def test_routes_to_normalized_data_source() -> None:
    generated = StubProvider(1.0)
    mt5 = StubProvider(2.0)

    router = MarketDataProviderRouter(
        {
            "generated": generated,
            " MT5 ": mt5,
        }
    )

    specification = build_specification("mt5")
    result = router.load(specification)

    assert result.iloc[0]["Close"] == 2.0
    assert generated.loaded == []
    assert mt5.loaded == [specification]


def test_copies_provider_registration() -> None:
    generated = StubProvider(1.0)
    registrations = {
        "generated": generated,
    }

    router = MarketDataProviderRouter(
        registrations
    )

    registrations.clear()

    result = router.load(
        build_specification("generated")
    )

    assert result.iloc[0]["Close"] == 1.0


def test_rejects_unsupported_data_source() -> None:
    router = MarketDataProviderRouter(
        {
            "generated": StubProvider(1.0),
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            "unsupported market data source: 'mt5'; "
            "registered sources: generated"
        ),
    ):
        router.load(
            build_specification("mt5")
        )


def test_rejects_duplicate_sources() -> None:
    with pytest.raises(
        ValueError,
        match="provider sources must be unique",
    ):
        MarketDataProviderRouter(
            {
                "mt5": StubProvider(1.0),
                " MT5 ": StubProvider(2.0),
            }
        )


def test_rejects_empty_registration() -> None:
    with pytest.raises(
        ValueError,
        match="providers must not be empty",
    ):
        MarketDataProviderRouter({})
