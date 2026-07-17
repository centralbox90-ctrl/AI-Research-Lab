from datetime import datetime

from src.core.snapshot import (
    BarIdentity,
    MarketData,
    MarketSnapshot
)



def create_snapshot(row):
    """
    Создает MarketSnapshot
    из одной строки DataFrame.
    """


    identity = BarIdentity(

        bar_id=row["bar_id"],

        symbol=row["symbol"],

        timeframe=row["timeframe"],

        timestamp=row.name
    )


    market = MarketData(

        open=float(row["Open"]),

        high=float(row["High"]),

        low=float(row["Low"]),

        close=float(row["Close"]),

        volume=float(row["Volume"])
    )


    snapshot = MarketSnapshot(

        identity=identity,

        market=market
    )


    return snapshot