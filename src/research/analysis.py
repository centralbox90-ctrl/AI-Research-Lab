from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Analysis:
    """
    Анализ свидетельств, полученных в ходе исследования.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    evidence_ids: list[str] = field(default_factory=list)

    title: str = ""

    findings: dict[str, Any] = field(default_factory=dict)

    interpretation: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def add_evidence(self, evidence_id: str) -> None:
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

    def summary(self) -> str:
        return (
            f"Analysis: {self.title}\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evidence: {len(self.evidence_ids)}\n"
            f"Findings: {len(self.findings)}\n"
            f"Interpretation: {self.interpretation or 'None'}"
        )