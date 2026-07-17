from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class ContradictionEvaluation:
    """
    Оценка противоречий между исследовательскими сигналами.

    Не является статистической или robustness оценкой.

    Модель хранит результат проверки согласованности между:

    - направлением среднего результата;
    - statistical significance;
    - robustness signal.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    is_evaluated: bool = False
    has_contradiction: bool = False

    observed_direction: str | None = None

    statistically_significant: bool | None = None
    robust: bool | None = None

    significance_robustness_conflict: bool | None = None
    direction_robustness_conflict: bool | None = None

    contradiction_count: int = 0

    warnings: list[str] = field(default_factory=list)

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Contradiction Evaluation\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evaluated: {self.is_evaluated}\n"
            f"Has contradiction: {self.has_contradiction}\n"
            f"Observed direction: {self.observed_direction}\n"
            f"Statistically significant: "
            f"{self.statistically_significant}\n"
            f"Robust: {self.robust}\n"
            f"Significance robustness conflict: "
            f"{self.significance_robustness_conflict}\n"
            f"Direction robustness conflict: "
            f"{self.direction_robustness_conflict}\n"
            f"Contradiction count: {self.contradiction_count}\n"
            f"Warnings: {len(self.warnings)}"
        )