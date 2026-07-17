from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import ResearchStatus


@dataclass
class ResearchPlan:
    """
    План исследования, связывающий вопрос, гипотезы и эксперименты.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    title: str = ""

    hypothesis_ids: list[str] = field(default_factory=list)

    experiment_ids: list[str] = field(default_factory=list)

    status: ResearchStatus = ResearchStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    notes: str = ""

    def add_hypothesis(self, hypothesis_id: str) -> None:
        if hypothesis_id not in self.hypothesis_ids:
            self.hypothesis_ids.append(hypothesis_id)

    def add_experiment(self, experiment_id: str) -> None:
        if experiment_id not in self.experiment_ids:
            self.experiment_ids.append(experiment_id)

    def summary(self) -> str:
        return (
            f"Research Plan: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Hypotheses: {len(self.hypothesis_ids)}\n"
            f"Experiments: {len(self.experiment_ids)}\n"
            f"Status: {self.status}"
        )