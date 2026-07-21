from __future__ import annotations

from src.indicators.series import IndicatorSeries
from src.signals.registry import SignalRuleRegistry
from src.signals.signal import MarketSignal


class SignalGenerationService:
    """
    Generates market signals using registered rules.
    """

    def __init__(
        self,
        registry: SignalRuleRegistry,
    ) -> None:
        self._registry = registry

    def generate(
        self,
        *,
        rule_id: str,
        series: IndicatorSeries,
        observations: tuple[int, ...],
    ) -> tuple[MarketSignal, ...]:

        rule = self._registry.get(
            rule_id,
        )

        return rule.generate(
            series,
            observations,
        )