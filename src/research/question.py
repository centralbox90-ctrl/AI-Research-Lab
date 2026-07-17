from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import ResearchStatus, ResearchType


@dataclass
class Question:
    """
    Исследовательский вопрос.

    Отправная точка исследования в AI Research Lab.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    title: str = ""

    description: str = ""

    research_type: ResearchType = ResearchType.HYPOTHESIS_TEST

    status: ResearchStatus = ResearchStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Question: {self.title}\n"
            f"ID: {self.id}\n"
            f"Type: {self.research_type}\n"
            f"Status: {self.status}\n"
            f"Tags: {', '.join(self.tags)}"
        )