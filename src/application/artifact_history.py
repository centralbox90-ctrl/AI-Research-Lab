from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ArtifactHistoryEntry:
    artifact_id: str

    previous_artifact_id: Optional[str]

    event_type: str

    description: Optional[str]

    created_at: datetime