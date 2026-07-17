from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class ExperimentResult:
    """
    Результат выполненного исследовательского эксперимента.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    success: bool = False

    metrics: dict[str, float] = field(default_factory=dict)

    observations: dict[str, Any] = field(default_factory=dict)

    conclusion: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        metrics = ", ".join(
            f"{name}={value}"
            for name, value in self.metrics.items()
        ) or "None"

        return (
            f"Experiment Result: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Success: {self.success}\n"
            f"Metrics: {metrics}\n"
            f"Conclusion: {self.conclusion or 'None'}"
        )