from abc import ABC, abstractmethod


class BaseIndicator(ABC):
    """
    Базовый класс любого индикатора.

    Каждый новый индикатор наследуется от него.
    """

    def __init__(self, config):
        self.config = config

    @property
    @abstractmethod
    def name(self):
        """
        Имя индикатора.
        """
        pass

    @abstractmethod
    def calculate(self, snapshot, history):
        """
        Расчет значения индикатора.

        snapshot - текущий бар
        history - история предыдущих баров
        """
        pass