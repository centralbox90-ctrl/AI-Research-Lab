from datetime import datetime, timezone

import pandas as pd
import pytest

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
from src.research.research_environment_builder import (
    MissingDatasetFingerprintError,
)
from src.application import (
    CodeVersionProvider,
    MarketResearchContextFactory,
    ResearchRuntimeConfiguration,
    StaticCodeVersionProvider,
)
def test_factory_uses_code_version_provider() -> None:
    context = build_factory(
        random_seed=42,
        code_version="runtime:old",
        code_version_provider=(
            StaticCodeVersionProvider(
                "git:new123",
            )
        ),
    ).create(
        specification=build_specification(),
        market_data=build_fingerprinted_market_data(),
    )

    assert (
        context.environment.code_version
        == "git:new123"
    )
def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Context factory question",
        question_description=(
            "Build a reproducible market research context."
        ),
        hypothesis_title="Context factory is valid",
        hypothesis_description=(
            "Canonical market data and assumptions produce "
            "a reproducible research context."
        ),
        expected_result=(
            "A valid ResearchContext is returned."
        ),
        experiment_title="Context factory experiment",
        experiment_description=(
            "Create a research context from market data."
        ),
        data_source="test",
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
        entry_rule="current_bar_close",
        exit_rule="policy_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "indicator": "williams",
            "period": 14,
        },
    )


def build_fingerprinted_market_data() -> pd.DataFrame:
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
            ],
            "open": [1.0, 1.1],
            "high": [1.1, 1.2],
            "low": [0.9, 1.0],
            "close": [1.05, 1.15],
            "tick_volume": [100, 110],
        }
    )

    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(raw)
    )

    MarketDatasetFingerprinter().attach(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    return canonical


def build_runtime_configuration(
    *,
    random_seed: int = 42,
) -> ResearchRuntimeConfiguration:
    return ResearchRuntimeConfiguration(
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=random_seed,
    )


def build_factory(
    *,
    random_seed: int = 42,
    code_version: str = "git:abc123",
    code_version_provider: (
        CodeVersionProvider | None
    ) = None,
) -> MarketResearchContextFactory:
    return MarketResearchContextFactory(
        runtime_configuration=(
            ResearchRuntimeConfiguration(
                code_version=code_version,
                executor_version="backtest-engine:v1",
                statistical_method_version="statistics:v1",
                random_seed=random_seed,
            )
        ),
        code_version_provider=code_version_provider,
    )

def test_factory_builds_reproducible_context() -> None:
    data = build_fingerprinted_market_data()

    context = build_factory().create(
        specification=build_specification(),
        market_data=data,
    )

    assert (
        context.environment.dataset_fingerprint
        == data.attrs["dataset_fingerprint"]
    )

    assert (
        context.environment.assumption_set_fingerprint
        == context.assumptions.fingerprint()
    )

    assert context.environment.code_version == "git:abc123"

    assert (
        context.environment.executor_version
        == "backtest-engine:v1"
    )

    assert (
        context.environment.statistical_method_version
        == "statistics:v1"
    )

    assert context.environment.random_seed == 42


def test_factory_uses_runtime_configuration_seed() -> None:
    context = build_factory(
        random_seed=42,
    ).create(
        specification=build_specification(),
        market_data=build_fingerprinted_market_data(),
    )

    assert context.environment.random_seed == 42


def test_factory_builds_market_assumptions() -> None:
    context = build_factory().create(
        specification=build_specification(),
        market_data=build_fingerprinted_market_data(),
    )

    assert context.assumptions.get(
        "scope.symbol"
    ).value == "EURUSD"

    assert context.assumptions.get(
        "execution.stop_loss_percent"
    ).value == 1.0


def test_factory_rejects_dataset_without_fingerprint() -> None:
    data = (
        MarketDatasetCanonicalizer()
        .canonicalize(
            pd.DataFrame(
                {
                    "timestamp": [
                        datetime(
                            2024,
                            1,
                            1,
                            tzinfo=timezone.utc,
                        )
                    ],
                    "open": [1.0],
                    "high": [1.1],
                    "low": [0.9],
                    "close": [1.05],
                    "tick_volume": [100],
                }
            )
        )
    )

    with pytest.raises(
        MissingDatasetFingerprintError,
    ):
        build_factory().create(
            specification=build_specification(),
            market_data=data,
        )


def test_factory_rejects_invalid_runtime_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="code_version",
    ):
        ResearchRuntimeConfiguration(
            code_version="",
            executor_version="backtest-engine:v1",
            statistical_method_version="statistics:v1",
            random_seed=42,
        )