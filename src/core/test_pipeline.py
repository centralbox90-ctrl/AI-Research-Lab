from src.data.loader import generate_market_data

from src.core.snapshot_factory import create_snapshot

from src.core.event_bus import EventBus

from src.storage.store_listener import StoreListener

from src.indicators.listener import IndicatorListener

from src.indicators.williams import WilliamsIndicator



def main():

    # Генерируем тестовый рынок

    data = generate_market_data(
        symbol="BTCUSDT",
        timeframe="1h",
        bars=20
    )


    # Создаем шину событий

    bus = EventBus()


    # Создаем модули

    indicator_listener = IndicatorListener()

    williams = WilliamsIndicator(
        period=14
    )

    storage = StoreListener()



    # Подключаем модули

    bus.subscribe(
        indicator_listener
    )

    bus.subscribe(
        williams
    )

    bus.subscribe(
        storage
    )



    # Передаем каждый бар через систему

    for index, row in data.iterrows():

        snapshot = create_snapshot(row)

        bus.publish(
            snapshot
        )



    # Проверяем хранилище

    store = storage.get_store()


    print()

    print(
        "Сохранено баров:",
        store.count()
    )


    print()

    print(
        "Последние бары и индикаторы:"
    )


    for snapshot in store.get_all():

        print(
            snapshot.identity.bar_id,
            "Close:",
            snapshot.market.close,
            "Indicators:",
            snapshot.indicators.all()
        )



if __name__ == "__main__":

    main()