from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class ResearchExecution:
    """
    Represents one research execution lifecycle.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    question_id: str = ""

    hypothesis_id: str = ""

    experiment_id: str = ""

    specification_id: str = ""

    evidence_id: str = ""

    finding_id: str = ""

    knowledge_id: str = ""

    started_at: datetime = field(default_factory=datetime.now)

    completed_at: datetime | None = None

    status: str = "NEW"

    success: bool = False

    notes: str = ""

    result: Any | None = None

    error: str = ""

    def complete(
        self,
        result: Any | None = None,
    ) -> None:
        """
        Marks the execution as successfully completed.
        """

        self.result = result
        self.success = True
        self.status = "COMPLETED"
        self.completed_at = datetime.now()

    def fail(
        self,
        error: BaseException | str,
    ) -> None:
        """
        Marks the execution as failed.
        """

        self.error = str(error)
        self.success = False
        self.status = "FAILED"
        self.completed_at = datetime.now()

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def duration(self) -> float | None:
        if self.completed_at is None:
            return None

        return (
            self.completed_at - self.started_at
        ).total_seconds()