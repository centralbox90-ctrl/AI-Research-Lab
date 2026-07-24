import pandas as pd

from src.data.loader import generate_market_data


def test_generates_deterministic_market_data(
) -> None:
    first = generate_market_data(
        symbol="BTCUSDT",
        timeframe="1h",
        bars=10,
    )
    second = generate_market_data(
        symbol="BTCUSDT",
        timeframe="1h",
        bars=10,
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_generates_valid_ohlc_and_identity(
) -> None:
    data = generate_market_data(
        symbol="EURUSD",
        timeframe="H1",
        bars=10,
    )

    assert tuple(data.columns) == (
        "symbol",
        "timeframe",
        "bar_id",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    )
    assert data.index.is_monotonic_increasing
    assert data.index.is_unique
    assert data["bar_id"].is_unique
    assert (data["High"] >= data["Open"]).all()
    assert (data["High"] >= data["Close"]).all()
    assert (data["Low"] <= data["Open"]).all()
    assert (data["Low"] <= data["Close"]).all()
    assert (data["Volume"] >= 0).all()