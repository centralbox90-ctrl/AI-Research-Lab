from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.prepared_market_backtest_executor import (
    PreparedMarketBacktestExecutor,
)
from src.research import Experiment


class FakeSignalProvider:
    def __init__(self) -> None:
        self.received_data = None
        self.received_specification = None

    def generate(
        self,
        data,
        specification,
    ):
        self.received_data = data
        self.received_specification = specification

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
        question_title="Prepared executor question",
        question_description=(
            "Execute a backtest from already loaded data."
        ),
        hypothesis_title="Prepared executor works",
        hypothesis_description=(
            "A prepared executor can run without loading data."
        ),
        expected_result="One profitable trade.",
        experiment_title="Prepared backtest",
        experiment_description=(
            "Execute using an existing market dataset."
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


def build_market_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": [
                100.0,
                103.0,
                103.0,
            ],
            "High": [
                100.0,
                103.0,
                103.0,
            ],
            "Low": [
                100.0,
                102.0,
                103.0,
            ],
        }
    )


def test_prepared_executor_runs_without_data_provider() -> None:
    signal_provider = FakeSignalProvider()
    market_data = build_market_data()

    executor = PreparedMarketBacktestExecutor(
        specification=build_specification(),
        market_data=market_data,
        signal_provider=signal_provider,
    )

    experiment = Experiment(
        title="prepared executor test",
    )

    result = executor(experiment)

    assert signal_provider.received_data is market_data
    assert result.experiment_id == experiment.id
    assert result.metrics["total_trades"] == 1
    assert result.success is True
    assert result.observations["exit_reasons"] == [
        "take_profit",
    ]


def test_prepared_executor_rejects_empty_market_data() -> None:
    with pytest.raises(
        ValueError,
        match="market_data cannot be empty",
    ):
        PreparedMarketBacktestExecutor(
            specification=build_specification(),
            market_data=pd.DataFrame(),
            signal_provider=FakeSignalProvider(),
        )