from src.data.loader import generate_market_data

from src.core.snapshot_factory import create_snapshot



data = generate_market_data(
    symbol="BTCUSDT",
    timeframe="1h",
    bars=3
)


for index, row in data.iterrows():

    snapshot = create_snapshot(row)


    print(
        snapshot.identity.bar_id,
        snapshot.identity.timeframe,
        snapshot.market.close
    )