from dataclasses import dataclass

from src.application.confidence_evolution import (
    ConfidenceEvolution,
)
from src.application.evidence_evolution import (
    EvidenceEvolution,
)
from src.application.hypothesis_evolution import (
    HypothesisEvolution,
)


@dataclass(frozen=True)
class ArtifactComparison:
    artifact_a_id: str

    artifact_b_id: str

    hypothesis_evolution: HypothesisEvolution

    evidence_evolution: EvidenceEvolution

    confidence_evolution: ConfidenceEvolution