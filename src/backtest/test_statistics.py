import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.statistics import Statistics


def test_statistics_calculates_backtest_metrics() -> None:
    data = pd.DataFrame(
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

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
    )

    stats = Statistics(trades).calculate()

    assert stats["total_trades"] == 1
    assert stats["buy_trades"] == 1
    assert stats["sell_trades"] == 0
    assert stats["win_rate"] == 100.0
    assert stats["net_profit"] == 10.0
