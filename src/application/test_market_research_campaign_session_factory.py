from datetime import datetime, timezone

import pandas as pd

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.market_dataset_quality import (
    MarketDatasetQualityAnalyzer,
)

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
    ResearchRuntimeConfiguration,
)
from src.research.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_research_campaign_session_factory import (
    MarketResearchCampaignSessionFactory,
)


class CountingMarketDataProvider:
    def __init__(self) -> None:
        self.load_count = 0
        self.last_data: pd.DataFrame | None = None

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> CanonicalMarketDataset:
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

        fingerprint = (
            MarketDatasetFingerprinter().attach(
                canonical,
                DatasetFingerprintContext(
                    symbol=specification.symbol,
                    timeframe=specification.timeframe,
                ),
            )
        )

        quality_report = (
            MarketDatasetQualityAnalyzer().analyze(
                canonical
            )
        )

        self.last_data = canonical

        return CanonicalMarketDataset(
            data=canonical,
            fingerprint=fingerprint,
            quality_report=quality_report,
        )


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


def build_specification(
    experiment_title: str,
) -> MarketExperimentSpecification:
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
        experiment_title=experiment_title,
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





def test_factory_builds_campaign_from_two_specifications() -> None:
    data_provider = CountingMarketDataProvider()

    factory = MarketResearchCampaignSessionFactory(
        data_provider=data_provider,
        signal_provider=FakeSignalProvider(),
        context_factory=build_context_factory(),
    )

    specification_a = build_specification(
        "Campaign experiment A",
    )

    specification_b = build_specification(
        "Campaign experiment B",
    )

    session = factory.create(
        (
            specification_a,
            specification_b,
        )
    )

    assert data_provider.load_count == 2

    assert len(session.contexts) == 2
    assert len(session.experiments) == 2

    assert (
        session.contexts[0].specification
        is specification_a
    )

    assert (
        session.contexts[1].specification
        is specification_b
    )

    assert (
        session.experiments[0].hypothesis_id
        == session.hypothesis.id
    )

    assert (
        session.experiments[1].hypothesis_id
        == session.hypothesis.id
    )

    assert (
        session.experiments[0].title
        == "Campaign experiment A"
    )
    
    assert (
        session.campaign.hypothesis_id
        == session.hypothesis.id
    )

    assert session.campaign.experiment_ids == [
        experiment.id
        for experiment in session.experiments
    ] 

    assert (
        session.experiments[1].title
        == "Campaign experiment B"
    )
