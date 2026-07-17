from src.indicators.registry import IndicatorRegistry


class IndicatorEngine:
    """
    Центральный движок индикаторов.

    Получает новый бар и передает его
    всем зарегистрированным индикаторам.
    """

    def __init__(self):

        self.registry = IndicatorRegistry()

        self.history = []

    def register(self, indicator):

        self.registry.register(indicator)

    def on_bar(self, snapshot):

        self.history.append(snapshot)

        for indicator in self.registry.all():

            indicator.calculate(
                snapshot,
                self.history
            )