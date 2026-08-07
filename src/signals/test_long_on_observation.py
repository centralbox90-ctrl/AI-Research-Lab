import pytest

from src.signals.implementations.long_on_observation import (
    LongOnObservationRule,
)
from src.signals.signal import (
    MarketSignalDirection,
)


class StubSeries:
    def __init__(self, length: int) -> None:
        self._length = length

    def __len__(self) -> int:
        return self._length


def test_converts_any_observation_to_long() -> None:
    signals = LongOnObservationRule().generate(
        StubSeries(3),
        (-1, 0, 1),
    )

    assert tuple(
        signal.value
        for signal in signals
    ) == (
        MarketSignalDirection.LONG,
        MarketSignalDirection.NEUTRAL,
        MarketSignalDirection.LONG,
    )


def test_rejects_length_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match="length mismatch",
    ):
        LongOnObservationRule().generate(
            StubSeries(2),
            (1,),
        )


def test_rejects_invalid_observation() -> None:
    with pytest.raises(
        ValueError,
        match="only -1, 0 or 1",
    ):
        LongOnObservationRule().generate(
            StubSeries(1),
            (2,),
        )


def test_rsi_declares_long_observation_rule() -> None:
    from src.indicators.implementations.rsi import (
        INDICATOR,
    )

    assert INDICATOR.research_space is not None

    assert (
        "long_on_observation"
        in INDICATOR.research_space.signal_rule_ids
    )