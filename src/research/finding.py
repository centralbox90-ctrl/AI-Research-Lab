from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Finding:
    """
    Вывод, полученный в результате выполнения исследования.

    Finding представляет собой интерпретацию полученных доказательств
    относительно конкретной исследовательской гипотезы.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    hypothesis_id: str = ""

    experiment_id: str = ""

    evidence_id: str = ""

    title: str = ""

    conclusion: str = ""

    supports_hypothesis: bool = False

    confidence: float = 0.0

    created_at: datetime = field(default_factory=datetime.now)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Finding: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evidence: {self.evidence_id}\n"
            f"Supports hypothesis: {self.supports_hypothesis}\n"
            f"Confidence: {self.confidence}\n"
            f"Conclusion: {self.conclusion or 'None'}"
        )