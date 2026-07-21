from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class MarketSignalDirection(IntEnum):
    """
    Normalized market signal values.
    """

    SHORT = -1
    NEUTRAL = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class MarketSignal:
    """
    One generated market signal.
    """

    value: MarketSignalDirection

    def __post_init__(self) -> None:
        if not isinstance(
            self.value,
            MarketSignalDirection,
        ):
            raise TypeError(
                "value must be MarketSignalDirection"
            )