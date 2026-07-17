from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HypothesisEvolution:
    previous_hypothesis: Optional[str]

    current_hypothesis: str

    change_reason: Optional[str]