from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class NextExperimentSelection:
    """
    Рекомендация следующего исследовательского действия.

    Selection не определяет, поддержана ли гипотеза.
    Он описывает наиболее полезный следующий research action
    на основании gaps текущего scientific pipeline.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    hypothesis_id: str = ""

    is_selected: bool = False

    action: str = "none"
    priority: str = "unknown"

    reason: str = ""

    target_requirement: str | None = None

    evidence_strength_score: float | None = None
    evidence_strength_level: str | None = None

    failed_requirements: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    basis: str = ""
    notes: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        return (
            f"Next Experiment Selection\n"
            f"ID: {self.id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Selected: {self.is_selected}\n"
            f"Action: {self.action}\n"
            f"Priority: {self.priority}\n"
            f"Target requirement: {self.target_requirement or 'None'}\n"
            f"Evidence strength: "
            f"{self.evidence_strength_score}\n"
            f"Evidence level: "
            f"{self.evidence_strength_level or 'None'}\n"
            f"Failed requirements: "
            f"{len(self.failed_requirements)}\n"
            f"Recommendations: {len(self.recommendations)}\n"
            f"Warnings: {len(self.warnings)}"
        )