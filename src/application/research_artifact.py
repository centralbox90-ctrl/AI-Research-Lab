from dataclasses import dataclass
from typing import Any

from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.artifact_history import (
    ArtifactHistoryEntry,
)
from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.artifact_metadata import (
    ArtifactMetadata,
)


@dataclass(frozen=True)
class ResearchArtifact:
    metadata: ArtifactMetadata

    lineage: ArtifactLineage | None

    history: list[ArtifactHistoryEntry]

    comparisons: list[ArtifactComparison]

    result: Any
    evaluation: Any
    conclusion: Any