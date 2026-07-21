from __future__ import annotations

from src.signals.descriptor import (
    SignalRuleDescriptor,
)
from src.signals.implementations.indicator import (
    IndicatorSignalRule,
)


SIGNAL_RULE = SignalRuleDescriptor(
    rule_id="indicator_direction",
    version=1,
    rule=IndicatorSignalRule(),
)