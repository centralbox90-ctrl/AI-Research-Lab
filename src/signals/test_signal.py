from dataclasses import FrozenInstanceError

import pytest

from src.signals.signal import (
    MarketSignal,
    MarketSignalDirection,
)


def test_market_signal_direction_has_canonical_values() -> None:
    assert MarketSignalDirection.SHORT.value == -1
    assert MarketSignalDirection.NEUTRAL.value == 0
    assert MarketSignalDirection.LONG.value == 1


@pytest.mark.parametrize(
    "direction",
    [
        MarketSignalDirection.SHORT,
        MarketSignalDirection.NEUTRAL,
        MarketSignalDirection.LONG,
    ],
)
def test_market_signal_accepts_direction(
    direction: MarketSignalDirection,
) -> None:
    signal = MarketSignal(value=direction)

    assert signal.value is direction


@pytest.mark.parametrize(
    "invalid_value",
    [
        -1,
        0,
        1,
        True,
        False,
        None,
        "LONG",
    ],
)
def test_market_signal_rejects_non_direction_values(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="value must be MarketSignalDirection",
    ):
        MarketSignal(value=invalid_value)


def test_market_signal_is_frozen() -> None:
    signal = MarketSignal(
        value=MarketSignalDirection.NEUTRAL,
    )

    with pytest.raises(FrozenInstanceError):
        signal.value = MarketSignalDirection.LONG


def test_market_signal_uses_value_equality() -> None:
    assert MarketSignal(
        MarketSignalDirection.LONG,
    ) == MarketSignal(
        MarketSignalDirection.LONG,
    )

    assert MarketSignal(
        MarketSignalDirection.LONG,
    ) != MarketSignal(
        MarketSignalDirection.SHORT,
    )
