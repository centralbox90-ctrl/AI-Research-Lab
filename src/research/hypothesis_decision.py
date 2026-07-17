from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class HypothesisDecision:
    """
    Финальное научное решение о поддержке гипотезы.

    Объединяет результаты отдельных evaluation layers:

    - basic result validation;
    - statistical evaluation;
    - robustness evaluation;
    - contradiction evaluation.

    Не выполняет собственные статистические расчёты.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""
    hypothesis_id: str = ""

    is_evaluated: bool = False
    is_supported: bool = False

    result_is_valid: bool | None = None
    statistically_significant: bool | None = None
    robust: bool | None = None
    has_contradiction: bool | None = None

    confidence: float = 0.0

    failed_requirements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    basis: str = ""
    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Hypothesis Decision\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Evaluated: {self.is_evaluated}\n"
            f"Supported: {self.is_supported}\n"
            f"Result valid: {self.result_is_valid}\n"
            f"Statistically significant: "
            f"{self.statistically_significant}\n"
            f"Robust: {self.robust}\n"
            f"Has contradiction: {self.has_contradiction}\n"
            f"Confidence: {self.confidence}\n"
            f"Failed requirements: {len(self.failed_requirements)}\n"
            f"Warnings: {len(self.warnings)}"
        )