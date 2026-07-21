from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.indicators.series import IndicatorSeries
from src.signals.signal import MarketSignal


class SignalRuleProtocol(Protocol):

    def generate(
        self,
        series: IndicatorSeries,
        observations: tuple[int, ...],
    ) -> tuple[MarketSignal, ...]:
        ...


@dataclass(frozen=True, slots=True)
class SignalRuleDescriptor:
    """
    Registered signal rule plugin.
    """

    rule_id: str
    version: int
    rule: SignalRuleProtocol

    def __post_init__(self) -> None:

        if not self.rule_id.strip():
            raise ValueError(
                "rule_id must not be empty"
            )

        if self.version < 1:
            raise ValueError(
                "version must be positive"
            )

        if not callable(
            getattr(
                self.rule,
                "generate",
                None,
            )
        ):
            raise TypeError(
                "rule must implement generate()"
            )