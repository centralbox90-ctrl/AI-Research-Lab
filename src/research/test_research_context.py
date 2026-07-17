from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.research.assumption import (
    AssumptionSet,
)
from src.research.research_context import (
    ResearchContext,
)
from src.research.research_environment import (
    ResearchEnvironmentRef,
)


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Research context question",
        question_description=(
            "Validate the research execution context."
        ),
        hypothesis_title="Research context is valid",
        hypothesis_description=(
            "A matching environment and dataset form "
            "a valid research context."
        ),
        expected_result=(
            "The context is created successfully."
        ),
        experiment_title="Research context experiment",
        experiment_description=(
            "Build an immutable research context."
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
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def build_market_data() -> pd.DataFrame:
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


def build_environment(
    dataset_fingerprint: str,
) -> ResearchEnvironmentRef:
    return ResearchEnvironmentRef(
        dataset_fingerprint=dataset_fingerprint,
        assumption_set_fingerprint="assumptions:001",
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )


def build_assumptions() -> AssumptionSet:
    return AssumptionSet(
        id="assumption-set:001",
        assumptions=(),
    )

def test_research_context_accepts_matching_environment() -> None:
    market_data = build_market_data()

    context = ResearchContext(
        specification=build_specification(),
        environment=build_environment(
            market_data.attrs["dataset_fingerprint"]
        ),
        market_data=market_data,
        assumptions=build_assumptions(),
    )

    assert (
        context.environment.dataset_fingerprint
        == context.market_data.attrs[
            "dataset_fingerprint"
        ]
    )


def test_research_context_rejects_empty_market_data() -> None:
    empty = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="market_data cannot be empty",
    ):
        ResearchContext(
            specification=build_specification(),
            environment=build_environment(
                "dataset:001"
            ),
            market_data=empty,
            assumptions=build_assumptions(),
        )


def test_research_context_rejects_missing_fingerprint() -> None:
    data = build_market_data()
    data.attrs.pop("dataset_fingerprint")

    with pytest.raises(
        ValueError,
        match="fingerprinted canonical dataset",
    ):
        ResearchContext(
            specification=build_specification(),
            environment=build_environment(
                "dataset:001"
            ),
            market_data=data,
            assumptions=build_assumptions(),
        )


def test_research_context_rejects_mismatched_environment() -> None:
    data = build_market_data()

    with pytest.raises(
        ValueError,
        match="does not match supplied market dataset",
    ):
        ResearchContext(
            specification=build_specification(),
            environment=build_environment(
                "different-dataset"
            ),
            market_data=data,
            assumptions=build_assumptions(),
        )