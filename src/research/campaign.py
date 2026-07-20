from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from src.research.assumption import AssumptionSet
from src.research.hypothesis import ResearchHypothesis
from src.research.question import ResearchQuestion
from src.research.research_types import ResearchStatus
from src.research.specification import ResearchSpecification


@dataclass(frozen=True, slots=True)
class Campaign:
    """Immutable research campaign."""

    research_question: ResearchQuestion
    hypothesis: ResearchHypothesis
    assumption_set: AssumptionSet
    specifications: tuple[ResearchSpecification, ...]

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: ResearchStatus = ResearchStatus.NEW

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("id must not be empty.")

        if not self.specifications:
            raise ValueError(
                "specifications must not be empty."
            )

        if not isinstance(
            self.status,
            ResearchStatus,
        ):
            raise TypeError(
                "status must be a ResearchStatus."
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "research_question_id": self.research_question.id,
            "hypothesis_id": self.hypothesis.id,
            "assumption_set_id": self.assumption_set.id,
            "specification_fingerprints": [
                specification.fingerprint
                for specification in self.specifications
            ],
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }