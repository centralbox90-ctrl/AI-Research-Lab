from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class RobustnessEvaluation:
    """
    Оценка устойчивости результата эксперимента.

    Не является статистической оценкой и не определяет
    автоматически, подтверждена ли исследовательская гипотеза.

    Модель хранит результаты отдельных robustness checks.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    is_evaluated: bool = False
    is_robust: bool = False

    sample_size: int | None = None

    positive_observation_ratio: float | None = None
    negative_observation_ratio: float | None = None
    zero_observation_ratio: float | None = None

    first_half_mean: float | None = None
    second_half_mean: float | None = None
    mean_shift: float | None = None

    direction_consistent: bool | None = None

    warnings: list[str] = field(default_factory=list)

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Robustness Evaluation\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evaluated: {self.is_evaluated}\n"
            f"Robust: {self.is_robust}\n"
            f"Sample size: {self.sample_size}\n"
            f"Positive observation ratio: "
            f"{self.positive_observation_ratio}\n"
            f"Negative observation ratio: "
            f"{self.negative_observation_ratio}\n"
            f"Zero observation ratio: "
            f"{self.zero_observation_ratio}\n"
            f"First half mean: {self.first_half_mean}\n"
            f"Second half mean: {self.second_half_mean}\n"
            f"Mean shift: {self.mean_shift}\n"
            f"Direction consistent: {self.direction_consistent}\n"
            f"Warnings: {len(self.warnings)}"
        )