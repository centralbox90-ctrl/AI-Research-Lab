from dataclasses import dataclass
from datetime import datetime

@dataclass
class BarIdentity:
    """
    Уникальная информация о баре
    """

    bar_id: str

    symbol: str

    timeframe: str

    timestamp: datetime



@dataclass
class MarketData:
    """
    Сырые данные свечи
    """

    open: float

    high: float

    low: float

    close: float

    volume: float



@dataclass
class MarketSnapshot:
    """
    Полное состояние рынка на одном баре.

    Один объект = один бар.

    Все модули системы работают
    только через этот объект.
    """


    identity: BarIdentity


    market: MarketData


    