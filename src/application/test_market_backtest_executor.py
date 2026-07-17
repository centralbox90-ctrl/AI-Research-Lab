from datetime import datetime, timezone

import pandas as pd

from src.application.market_backtest_executor import (
    MarketBacktestExecutor,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research import Experiment


class FakeMarketDataProvider:

    def load(
        self,
        specification,
    ) -> pd.DataFrame:

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
                "AI_prediction": [
                    1,
                    1,
                    0,
                ],
            }
        )


class FakeSignalProvider:

    def generate(
        self,
        data,
        specification,
    ):
        return data


def build_specification():

    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Test market executor",
        question_description="Test execution",
        hypothesis_title="Positive market result",
        hypothesis_description="Test",
        expected_result="Positive trades",
        experiment_title="Backtest",
        experiment_description="Backtest execution",
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


def test_market_backtest_executor_runs_complete_execution():

    specification = build_specification()

    executor = MarketBacktestExecutor(
        specification=specification,
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeSignalProvider(),
    )

    experiment = Experiment(
        title="executor test",
    )

    result = executor(experiment)

    assert result.experiment_id == experiment.id
    assert result.metrics["total_trades"] == 1
    assert result.success is True
    assert result.observations["exit_reasons"] == [
        "take_profit",
    ]