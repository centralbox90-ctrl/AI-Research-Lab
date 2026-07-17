from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Conclusion:
    """
    Вывод исследования.

    Вывод может быть предварительным, если результат прошёл только
    базовую проверку и ещё не прошёл статистическую оценку,
    проверку устойчивости и поиск противоречий.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    analysis_id: str = ""

    hypothesis_id: str = ""

    title: str = ""

    statement: str = ""

    supported: bool = False

    confidence: float = 0.0

    is_provisional: bool = True

    basis: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Conclusion: {self.title}\n"
            f"ID: {self.id}\n"
            f"Analysis: {self.analysis_id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Supported: {self.supported}\n"
            f"Confidence: {self.confidence}\n"
            f"Provisional: {self.is_provisional}\n"
            f"Basis: {self.basis or 'None'}\n"
            f"Statement: {self.statement or 'None'}"
        )