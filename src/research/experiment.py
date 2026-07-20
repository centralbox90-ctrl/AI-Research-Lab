from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.research.research_types import ExperimentStatus


@dataclass
class Experiment:
    """
    Эксперимент для проверки исследовательской гипотезы.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    hypothesis_id: str = ""

    title: str = ""

    description: str = ""

    parameters: dict[str, Any] = field(default_factory=dict)

    status: ExperimentStatus = ExperimentStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    started_at: datetime | None = None

    completed_at: datetime | None = None

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        parameters = ", ".join(
            f"{name}={value}"
            for name, value in self.parameters.items()
        ) or "None"

        return (
            f"Experiment: {self.title}\n"
            f"ID: {self.id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Status: {self.status}\n"
            f"Parameters: {parameters}"
        )
