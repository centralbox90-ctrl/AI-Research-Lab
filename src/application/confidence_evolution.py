from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConfidenceEvolution:
    previous_confidence: float

    current_confidence: float

    change_reason: Optional[str]