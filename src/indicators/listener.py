class IndicatorListener:
    """
    Базовый слушатель индикаторов.
    Получает каждый MarketSnapshot
    через EventBus.
    """


    def on_bar(self, snapshot):

        print(
            "Indicator processing:",
            snapshot.identity.bar_id
        )