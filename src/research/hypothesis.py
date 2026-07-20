from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import HypothesisStatus


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """
    Проверяемая гипотеза исследования.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    title: str = ""

    description: str = ""

    expected_result: str = ""

    status: HypothesisStatus = HypothesisStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Hypothesis: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Expected: {self.expected_result}\n"
            f"Status: {self.status}"
        )


@dataclass(frozen=True, slots=True)
class ResearchHypothesis:
    """A testable statement linked to a research question."""

    research_question_id: str
    statement: str
    expected_direction: str
    target_metric: str
    null_condition: str
    alternative_condition: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: HypothesisStatus = HypothesisStatus.NEW

    def __post_init__(self) -> None:
        string_fields = {
            "id": self.id,
            "research_question_id": self.research_question_id,
            "statement": self.statement,
            "expected_direction": self.expected_direction,
            "target_metric": self.target_metric,
            "null_condition": self.null_condition,
            "alternative_condition": self.alternative_condition,
        }

        for name, value in string_fields.items():
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")

            if not value.strip():
                raise ValueError(f"{name} must not be empty.")

        if not isinstance(self.status, HypothesisStatus):
            raise TypeError(
                "status must be a HypothesisStatus."
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "research_question_id": (
                self.research_question_id
            ),
            "statement": self.statement,
            "expected_direction": self.expected_direction,
            "target_metric": self.target_metric,
            "null_condition": self.null_condition,
            "alternative_condition": (
                self.alternative_condition
            ),
            "status": self.status.value,
        }
