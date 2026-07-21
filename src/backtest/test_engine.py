import pandas as pd

from src.backtest.engine import BacktestEngine


def test_backtest_engine_accepts_canonical_market_data() -> None:
    data = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2026-01-01 00:00:00",
                    "2026-01-01 01:00:00",
                    "2026-01-01 02:00:00",
                ]
            ),
            "open": [100.0, 105.0, 110.0],
            "high": [101.0, 106.0, 111.0],
            "low": [99.0, 104.0, 109.0],
            "close": [100.0, 105.0, 110.0],
            "tick_volume": [10, 20, 30],
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
    assert trade.entry_time == pd.Timestamp(
        "2026-01-01 00:00:00"
    )
    assert trade.exit_time == pd.Timestamp(
        "2026-01-01 02:00:00"
    )
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.profit_percent == 10.0

