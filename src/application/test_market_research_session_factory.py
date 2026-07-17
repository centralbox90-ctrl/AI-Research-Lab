from datetime import datetime, timezone

import pandas as pd

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
    ResearchRuntimeConfiguration,
)
from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_research_session_factory import (
    MarketResearchSessionFactory,
)


class CountingMarketDataProvider:
    def __init__(self) -> None:
        self.load_count = 0
        self.last_data: pd.DataFrame | None = None

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        self.load_count += 1

        raw = pd.DataFrame(
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
                "open": [
                    100.0,
                    103.0,
                    103.0,
                ],
                "high": [
                    100.0,
                    103.0,
                    103.0,
                ],
                "low": [
                    100.0,
                    102.0,
                    103.0,
                ],
                "close": [
                    100.0,
                    103.0,
                    103.0,
                ],
                "tick_volume": [
                    100,
                    110,
                    120,
                ],
            }
        )

        canonical = (
            MarketDatasetCanonicalizer()
            .canonicalize(raw)
        )

        MarketDatasetFingerprinter().attach(
            canonical,
            DatasetFingerprintContext(
                symbol=specification.symbol,
                timeframe=specification.timeframe,
            ),
        )

        self.last_data = canonical

        return canonical


class FakeSignalProvider:
    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        prepared = data.copy()

        prepared["AI_prediction"] = [
            1,
            1,
            0,
        ]

        return prepared


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Session factory question",
        question_description=(
            "Build one reproducible market session."
        ),
        hypothesis_title="Session factory works",
        hypothesis_description=(
            "One dataset is shared by context and execution."
        ),
        expected_result="One profitable trade.",
        experiment_title="Session factory experiment",
        experiment_description=(
            "Build and execute a prepared session."
        ),
        data_source="test",
        symbol="BTCUSDT",
        timeframe="1H",
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
        entry_rule="rule",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def build_runtime_configuration() -> (
    ResearchRuntimeConfiguration
):
    return ResearchRuntimeConfiguration(
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )


def build_context_factory() -> (
    MarketResearchContextFactory
):
    return MarketResearchContextFactory(
        runtime_configuration=(
            build_runtime_configuration()
        ),
    )


def test_factory_loads_market_data_once() -> None:
    data_provider = CountingMarketDataProvider()

    factory = MarketResearchSessionFactory(
        data_provider=data_provider,
        signal_provider=FakeSignalProvider(),
        context_factory=build_context_factory(),
    )

    session = factory.create(
        build_specification(),
    )

    assert data_provider.load_count == 1

    assert (
        session.context.market_data
        is data_provider.last_data
    )

    assert (
        session.executor.market_data
        is data_provider.last_data
    )


def test_factory_builds_matching_environment() -> None:
    factory = MarketResearchSessionFactory(
        data_provider=CountingMarketDataProvider(),
        signal_provider=FakeSignalProvider(),
        context_factory=build_context_factory(),
    )

    session = factory.create(
        build_specification(),
    )

    assert (
        session.context.environment.dataset_fingerprint
        == session.context.market_data.attrs[
            "dataset_fingerprint"
        ]
    )

    assert (
        session.context.environment
        .assumption_set_fingerprint
        == session.context.assumptions.fingerprint()
    )

    assert (
        session.context.environment.code_version
        == "git:abc123"
    )

    assert (
        session.context.environment.executor_version
        == "backtest-engine:v1"
    )

    assert (
        session.context.environment
        .statistical_method_version
        == "statistics:v1"
    )

    assert (
        session.context.environment.random_seed
        == 42
    )


def test_created_session_executes_experiment() -> None:
    factory = MarketResearchSessionFactory(
        data_provider=CountingMarketDataProvider(),
        signal_provider=FakeSignalProvider(),
        context_factory=build_context_factory(),
    )

    session = factory.create(
        build_specification(),
    )

    result = session.execute()

    assert (
        result.experiment_id
        == session.experiment.id
    )

    assert result.metrics["total_trades"] == 1
    assert result.success is True