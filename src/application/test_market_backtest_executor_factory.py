from datetime import datetime, timezone

from src.application import (
    MarketBacktestExecutor,
    MarketBacktestExecutorFactory,
    MarketExperimentSpecification,
    MarketPositionDirection,
)


class FakeMarketDataProvider:
    pass


class FakeMarketSignalProvider:
    pass


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Question",
        question_description="Description",
        hypothesis_title="Hypothesis",
        hypothesis_description="Description",
        expected_result="Positive result",
        experiment_title="Experiment",
        experiment_description="Description",
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
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="entry_rule",
        exit_rule="exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def test_market_backtest_executor_factory_creates_executor() -> None:
    data_provider = FakeMarketDataProvider()
    signal_provider = FakeMarketSignalProvider()

    factory = MarketBacktestExecutorFactory(
        data_provider=data_provider,
        signal_provider=signal_provider,
    )

    executor = factory.create(
        build_specification(),
    )

    assert isinstance(
        executor,
        MarketBacktestExecutor,
    )

    assert executor.data_provider is data_provider
    assert executor.signal_provider is signal_provider