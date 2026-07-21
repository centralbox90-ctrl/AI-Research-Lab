import pandas as pd

from src.research.backtest_executor import BacktestExperimentExecutor
from src.research.experiment import Experiment


def test_backtest_executor_stores_trade_observations() -> None:
    experiment = Experiment(
        title="Backtest observations",
    )

    def data_provider(current_experiment: Experiment) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    "2026-01-01",
                    periods=3,
                    freq="h",
                ),
                "close": [100.0, 105.0, 110.0],
                "high": [101.0, 106.0, 111.0],
                "low": [99.0, 104.0, 109.0],
                "AI_prediction": [1, 1, 0],
            }
        )

    executor = BacktestExperimentExecutor(
        data_provider=data_provider,
        symbol="BTCUSDT",
        timeframe="1H",
    )

    result = executor(experiment)

    assert result.metrics["total_trades"] == 1
    assert result.observations["profit_percent"] == [10.0]
