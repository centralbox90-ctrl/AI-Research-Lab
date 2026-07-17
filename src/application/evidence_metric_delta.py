from dataclasses import dataclass
from typing import Any, Literal


EvidenceMetricDirection = Literal[
    "increased",
    "decreased",
    "unchanged",
    "added",
    "removed",
    "not_comparable",
]


@dataclass(frozen=True)
class EvidenceMetricDelta:
    metric_name: str
    previous_value: Any
    current_value: Any
    absolute_delta: float | None
    direction: EvidenceMetricDirection