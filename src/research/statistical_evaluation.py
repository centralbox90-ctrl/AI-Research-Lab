from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class StatisticalEvaluation:
    """
    Статистическая оценка результата эксперимента.

    Модель разделяет:

    - descriptive statistics;
    - uncertainty estimation;
    - inferential statistics;
    - решение о statistical significance.

    Наличие среднего значения или confidence interval само по себе
    не означает подтверждение исследовательской гипотезы.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    is_evaluated: bool = False
    is_significant: bool = False

    mean: float | None = None
    standard_deviation: float | None = None
    standard_error: float | None = None

    confidence_interval_lower: float | None = None
    confidence_interval_upper: float | None = None
    confidence_level: float | None = None

    null_mean: float | None = None
    alternative: str | None = None
    significance_level: float | None = None
    test_method: str | None = None
    test_statistic: float | None = None

    p_value: float | None = None
    effect_size: float | None = None

    sample_size: int | None = None

    warnings: list[str] = field(default_factory=list)

    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Statistical Evaluation\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Evaluated: {self.is_evaluated}\n"
            f"Significant: {self.is_significant}\n"
            f"Mean: {self.mean}\n"
            f"Standard deviation: {self.standard_deviation}\n"
            f"Standard error: {self.standard_error}\n"
            f"Confidence interval: "
            f"[{self.confidence_interval_lower}, "
            f"{self.confidence_interval_upper}]\n"
            f"Confidence level: {self.confidence_level}\n"
            f"Null mean: {self.null_mean}\n"
            f"Alternative: {self.alternative}\n"
            f"Significance level: {self.significance_level}\n"
            f"Test method: {self.test_method}\n"
            f"Test statistic: {self.test_statistic}\n"
            f"P-value: {self.p_value}\n"
            f"Effect size: {self.effect_size}\n"
            f"Sample size: {self.sample_size}\n"
            f"Warnings: {len(self.warnings)}"
        )