from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ArtifactLineage:
    parent_artifact_id: Optional[str]
    lineage_type: str
    change_description: Optional[str]
    created_from_experiment: Optional[str]