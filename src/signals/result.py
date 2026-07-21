from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.signals.signal import MarketSignal


@dataclass(frozen=True, slots=True)
class MarketSignalResult:
    """
    Result of converting observations into market signals.
    """

    signals: tuple[MarketSignal, ...]

    metadata: Mapping[str, Any] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "signals",
            tuple(self.signals),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )

        if not self.signals:
            raise ValueError(
                "signals must not be empty"
            )