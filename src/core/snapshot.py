from dataclasses import dataclass, field
from datetime import datetime

from src.core.state import (
    IndicatorState,
    FeatureState,
    AIState,
    TradeState
)



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


    indicators: IndicatorState = field(
        default_factory=IndicatorState
    )


    features: FeatureState = field(
        default_factory=FeatureState
    )


    ai: AIState = field(
        default_factory=AIState
    )


    trade: TradeState = field(
        default_factory=TradeState
    )