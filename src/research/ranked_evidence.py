from dataclasses import dataclass, field

from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.experiment import Experiment


@dataclass
class RankedEvidence:
    """
    Результат ранжирования эксперимента по силе evidence.

    Rank не является научным решением о поддержке гипотезы.
    Он используется только для сравнения завершённых экспериментов.
    """

    rank: int = 0

    experiment: Experiment | None = None

    evidence_strength_evaluation: (
        EvidenceStrengthEvaluation | None
    ) = None

    score: float = 0.0
    level: str = "unknown"

    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        experiment_id = (
            self.experiment.id
            if self.experiment is not None
            else "None"
        )

        return (
            f"Ranked Evidence\n"
            f"Rank: {self.rank}\n"
            f"Experiment: {experiment_id}\n"
            f"Score: {self.score}\n"
            f"Level: {self.level}\n"
            f"Warnings: {len(self.warnings)}"
        )