from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ArtifactMetadata:
    artifact_id: str
    schema_version: str
    created_at: datetime

    experiment_id: Optional[str]

    executor_type: Optional[str]
    executor_version: Optional[str]

    data_source: Optional[str]

    code_version: Optional[str]