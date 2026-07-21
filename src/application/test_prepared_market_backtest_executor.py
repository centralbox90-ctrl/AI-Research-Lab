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
        self.received_data: pd.DataFrame | None = None
        self.received_specification = None

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        self.received_data = data
        self.received_specification = specification
        
        result = data.copy()
        result["AI_prediction"] = 0

        if len(result) >= 1:
            result.loc[result.index[0], "AI_prediction"] = 1

        if len(result) >= 2:
            result.loc[result.index[1], "AI_prediction"] = 1

        return result


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
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "open": [100.0, 101.0, 103.0],
            "high": [100.0, 103.0, 103.0],
            "low": [100.0, 102.0, 103.0],
            "close": [100.0, 103.0, 103.0],
            "tick_volume": [100, 120, 110],
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