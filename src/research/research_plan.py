from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.research.research_types import ResearchStatus


@dataclass
class ResearchPlan:
    """
    High-level research plan.

    A plan organizes research campaigns around a question.
    Each campaign owns its hypothesis and experiments.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    question_id: str = ""

    title: str = ""

    campaign_ids: list[str] = field(
        default_factory=list
    )

    status: ResearchStatus = ResearchStatus.NEW

    created_at: datetime = field(
        default_factory=datetime.now
    )

    notes: str = ""

    def add_campaign(
        self,
        campaign_id: str,
    ) -> None:
        if campaign_id not in self.campaign_ids:
            self.campaign_ids.append(
                campaign_id
            )

    def summary(self) -> str:
        return (
            f"Research Plan: {self.title}\n"
            f"ID: {self.id}\n"
            f"Question: {self.question_id}\n"
            f"Campaigns: {len(self.campaign_ids)}\n"
            f"Status: {self.status}"
        )
