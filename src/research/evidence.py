from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Evidence:
    """
    Наблюдаемое свидетельство, полученное из эксперимента.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    experiment_id: str = ""

    title: str = ""

    data: dict[str, Any] = field(default_factory=dict)

    source: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Evidence: {self.title}\n"
            f"ID: {self.id}\n"
            f"Experiment: {self.experiment_id}\n"
            f"Source: {self.source or 'None'}\n"
            f"Data points: {len(self.data)}"
        )