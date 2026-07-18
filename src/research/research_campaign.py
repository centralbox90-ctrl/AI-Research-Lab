from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import ResearchStatus


@dataclass
class ResearchCampaign:
    """
    Represents an ongoing investigation of one hypothesis.

    A campaign may contain multiple experiments executed to
    validate, reject, or refine the hypothesis.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    title: str = ""

    hypothesis_id: str = ""

    experiment_ids: list[str] = field(
        default_factory=list
    )

    status: ResearchStatus = ResearchStatus.NEW

    created_at: datetime = field(
        default_factory=datetime.now
    )

    notes: str = ""

    def add_experiment(
        self,
        experiment_id: str,
    ) -> None:
        if experiment_id not in self.experiment_ids:
            self.experiment_ids.append(
                experiment_id
            )

    def start(self) -> None:
        if self.status != ResearchStatus.NEW:
            raise ValueError(
                "campaign can start only from NEW"
            )

        self.status = ResearchStatus.RUNNING

    def complete(self) -> None:
        if self.status != ResearchStatus.RUNNING:
            raise ValueError(
                "campaign can complete only from RUNNING"
            )

        if not self.experiment_ids:
            raise ValueError(
                "campaign cannot complete without experiments"
            )

        self.status = ResearchStatus.COMPLETED

    def fail(self) -> None:
        if self.status != ResearchStatus.RUNNING:
            raise ValueError(
                "campaign can fail only from RUNNING"
            )

        self.status = ResearchStatus.FAILED

    def summary(self) -> str:
        return (
            f"Research Campaign: {self.title}\n"
            f"ID: {self.id}\n"
            f"Hypothesis: {self.hypothesis_id}\n"
            f"Experiments: {len(self.experiment_ids)}\n"
            f"Status: {self.status}"
        )
