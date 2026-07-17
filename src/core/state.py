class IndicatorState:
    """
    Хранилище индикаторов.

    Пример:
    ADX14 = 25.4
    Williams_R = -30
    MACD = 0.12
    """


    def __init__(self):

        self.values = {}



    def set(self, name, value):

        self.values[name] = value



    def get(self, name, default=None):

        return self.values.get(
            name,
            default
        )



    def all(self):

        return self.values



class FeatureState:
    """
    Хранилище признаков для AI.
    """


    def __init__(self):

        self.values = {}



    def set(self, name, value):

        self.values[name] = value



    def get(self, name, default=None):

        return self.values.get(
            name,
            default
        )



    def all(self):

        return self.values



class AIState:
    """
    Состояние AI модели.
    """


    def __init__(self):

        self.prediction = None

        self.confidence = None

        self.model_version = None



class TradeState:
    """
    Состояние торговли.
    """


    def __init__(self):

        self.position = None

        self.entry_price = None

        self.stop_loss = None

        self.take_profit = None