from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class ExperimentEvaluation:
    """
    Научная оценка результата эксперимента.

    Не является результатом эксперимента и не определяет,
    подтверждена ли гипотеза окончательно.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    is_valid: bool = False

    evidence_strength: float = 0.0

    warnings: list[str] = field(default_factory=list)

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Experiment Evaluation\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Valid: {self.is_valid}\n"
            f"Evidence strength: {self.evidence_strength}\n"
            f"Warnings: {len(self.warnings)}"
        )