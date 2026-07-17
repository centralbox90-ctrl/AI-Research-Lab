from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import HypothesisStatus


@dataclass
class Hypothesis:
    """
    Проверяемая гипотеза исследования.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    title: str = ""

    description: str = ""

    expected_result: str = ""

    status: HypothesisStatus = HypothesisStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Hypothesis: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Expected: {self.expected_result}\n"
            f"Status: {self.status}"
        )