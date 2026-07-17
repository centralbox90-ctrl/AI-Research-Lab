from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class EvidenceStrengthEvaluation:
    """
    Итоговая оценка силы научного evidence.

    Объединяет уже рассчитанные исследовательские сигналы:

    - basic validation;
    - statistical significance;
    - p-value;
    - effect size;
    - robustness;
    - contradictions.

    Не выполняет собственные статистические расчёты.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    is_evaluated: bool = False

    score: float = 0.0
    level: str = "unknown"

    result_is_valid: bool | None = None
    statistically_significant: bool | None = None
    p_value: float | None = None
    effect_size: float | None = None
    robust: bool | None = None
    has_contradiction: bool | None = None

    component_scores: dict[str, float] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    basis: str = ""
    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Evidence Strength Evaluation\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evaluated: {self.is_evaluated}\n"
            f"Score: {self.score}\n"
            f"Level: {self.level}\n"
            f"Result valid: {self.result_is_valid}\n"
            f"Statistically significant: "
            f"{self.statistically_significant}\n"
            f"P-value: {self.p_value}\n"
            f"Effect size: {self.effect_size}\n"
            f"Robust: {self.robust}\n"
            f"Has contradiction: {self.has_contradiction}\n"
            f"Components: {len(self.component_scores)}\n"
            f"Warnings: {len(self.warnings)}"
        )