import pandas as pd

from src.backtest.engine import BacktestEngine


def test_backtest_engine_creates_trade() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 105.0, 110.0],
            "High": [101.0, 106.0, 111.0],
            "Low": [99.0, 104.0, 109.0],
            "AI_prediction": [1, 1, 0],
        }
    )

    trades = BacktestEngine().run(
        data=data,
        symbol="BTCUSDT",
        timeframe="1H",
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.symbol == "BTCUSDT"
    assert trade.timeframe == "1H"
    assert trade.side == "BUY"
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.profit_percent == 10.0