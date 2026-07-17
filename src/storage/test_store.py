from datetime import datetime

from src.core.snapshot import (
    BarIdentity,
    MarketData,
    MarketSnapshot
)

from src.storage.feature_store import FeatureStore



identity = BarIdentity(
    bar_id="bar_001",
    symbol="BTCUSDT",
    timeframe="1h",
    timestamp=datetime.now()
)


market = MarketData(
    open=100,
    high=105,
    low=98,
    close=103,
    volume=5000
)


snapshot = MarketSnapshot(
    identity=identity,
    market=market
)


store = FeatureStore()


store.save(snapshot)


print(
    "Количество баров:",
    store.count()
)


last = store.get_last()


print(
    "Последний бар:",
    last.identity.bar_id
)