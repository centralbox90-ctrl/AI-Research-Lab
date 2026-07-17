class IndicatorRegistry:
    """
    Хранилище всех зарегистрированных индикаторов.
    """

    def __init__(self):
        self._indicators = {}

    def register(self, indicator):
        self._indicators[indicator.name] = indicator

    def get(self, name):
        return self._indicators.get(name)

    def all(self):
        return self._indicators.values()

    def names(self):
        return list(self._indicators.keys())