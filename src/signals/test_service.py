from unittest.mock import Mock

import pytest

from src.indicators.series import IndicatorSeries
from src.signals.service import SignalGenerationService
from src.signals.signal import (
    MarketSignal,
    MarketSignalDirection,
)


def test_generate_resolves_rule_and_forwards_inputs() -> None:
    series = Mock(spec=IndicatorSeries)
    observations = (
        -1,
        0,
        1,
    )
    generated_signals = (
        MarketSignal(MarketSignalDirection.SHORT),
        MarketSignal(MarketSignalDirection.NEUTRAL),
        MarketSignal(MarketSignalDirection.LONG),
    )

    rule = Mock()
    rule.generate.return_value = generated_signals

    registry = Mock()
    registry.get.return_value = rule

    service = SignalGenerationService(registry)

    result = service.generate(
        rule_id="observation-direction",
        series=series,
        observations=observations,
    )

    registry.get.assert_called_once_with(
        "observation-direction",
    )
    rule.generate.assert_called_once_with(
        series,
        observations,
    )
    assert result is generated_signals


def test_generate_propagates_unknown_rule_error() -> None:
    registry = Mock()
    registry.get.side_effect = KeyError(
        "Unknown signal rule: missing",
    )

    service = SignalGenerationService(registry)

    with pytest.raises(
        KeyError,
        match="Unknown signal rule: missing",
    ):
        service.generate(
            rule_id="missing",
            series=Mock(spec=IndicatorSeries),
            observations=(),
        )


def test_generate_propagates_rule_error() -> None:
    rule = Mock()
    rule.generate.side_effect = ValueError(
        "Invalid observations",
    )

    registry = Mock()
    registry.get.return_value = rule

    service = SignalGenerationService(registry)

    with pytest.raises(
        ValueError,
        match="Invalid observations",
    ):
        service.generate(
            rule_id="failing-rule",
            series=Mock(spec=IndicatorSeries),
            observations=(1,),
        )
