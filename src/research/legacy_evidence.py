from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class LegacyEvidence:
    """
    Mutable evidence record used by the legacy ResearchEngine.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )
    experiment_id: str = ""
    title: str = ""
    data: dict[str, Any] = field(
        default_factory=dict
    )
    source: str = ""
    created_at: datetime = field(
        default_factory=datetime.now
    )
    tags: list[str] = field(
        default_factory=list
    )
    notes: str = ""
    question_id: str = ""
    hypothesis_id: str = ""
    observation_ids: list[str] = field(
        default_factory=list
    )
    description: str = ""
    supports_hypothesis: bool = False
    confidence: float = 0.0

    def summary(self) -> str:
        return (
            f"Evidence: {self.title}\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Source: {self.source or 'None'}\n"
            f"Data points: {len(self.data)}"
        )
