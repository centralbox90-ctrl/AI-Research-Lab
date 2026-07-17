from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Knowledge:
    """
    Знание или предварительный кандидат в знание,
    полученный в результате исследования.

    Предварительное знание ещё не прошло достаточную
    статистическую проверку, проверку устойчивости,
    воспроизводимости и противоречий.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    hypothesis_id: str = ""

    experiment_id: str = ""

    title: str = ""

    statement: str = ""

    confidence: float = 0.0

    is_provisional: bool = True

    basis: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Knowledge: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Confidence: {self.confidence}\n"
            f"Provisional: {self.is_provisional}\n"
            f"Basis: {self.basis or 'None'}\n"
            f"Statement: {self.statement or 'None'}"
        )