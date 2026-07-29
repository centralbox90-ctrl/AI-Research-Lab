from dataclasses import replace
from datetime import datetime, timezone

import pandas as pd

from src.application.canonical_market_data_provider import (
    CanonicalMarketDataProvider,
)
from src.application.generated_market_data_provider import (
    GeneratedMarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)


def build_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Can generated data replicate?",
        question_description=(
            "Test deterministic generated replications."
        ),
        hypothesis_title=(
            "Generated periods produce distinct datasets"
        ),
        hypothesis_description=(
            "Different declared periods should produce "
            "reproducible distinct datasets."
        ),
        expected_result=(
            "Each data identity has a stable dataset."
        ),
        experiment_title=(
            "Generated replication experiment"
        ),
        experiment_description=(
            "Load one deterministic generated period."
        ),
        data_source="generated",
        symbol="EURUSD",
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
        max_holding_bars=10,
    )


def test_repeats_the_same_data_identity(
) -> None:
    provider = GeneratedMarketDataProvider()
    specification = build_specification()

    first = provider.load(specification)
    repeated = provider.load(specification)

    pd.testing.assert_frame_equal(
        first,
        repeated,
    )


def test_generates_distinct_period_replications(
) -> None:
    provider = GeneratedMarketDataProvider()
    first_specification = build_specification()
    second_specification = replace(
        first_specification,
        start_at=datetime(
            2026,
            3,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2026,
            4,
            1,
            tzinfo=timezone.utc,
        ),
    )

    first = provider.load(
        first_specification
    )
    second = provider.load(
        second_specification
    )

    assert first.index[0] == pd.Timestamp(
        first_specification.start_at
    )
    assert second.index[0] == pd.Timestamp(
        second_specification.start_at
    )
    assert not first["Close"].equals(
        second["Close"]
    )
    assert len(first) == 744
    assert len(second) == 744

    canonical_provider = (
        CanonicalMarketDataProvider(
            provider
        )
    )
    first_dataset = canonical_provider.load(
        first_specification
    )
    second_dataset = canonical_provider.load(
        second_specification
    )

    assert (
        first_dataset
        .fingerprint
        .dataset_fingerprint
        != second_dataset
        .fingerprint
        .dataset_fingerprint
    )


def test_strategy_change_does_not_change_input_data(
) -> None:
    provider = GeneratedMarketDataProvider()
    specification = build_specification()
    changed_strategy = replace(
        specification,
        entry_rule="rsi < 25",
        take_profit_percent=3.0,
    )

    original = provider.load(
        specification
    )
    changed = provider.load(
        changed_strategy
    )

    pd.testing.assert_frame_equal(
        original,
        changed,
    )
