from typing import Any

from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.confidence_evolution import (
    ConfidenceEvolution,
)
from src.application.evidence_evolution import (
    EvidenceEvolution,
)
from src.application.evidence_metric_delta_builder import (
    EvidenceMetricDeltaBuilder,
)
from src.application.hypothesis_evolution import (
    HypothesisEvolution,
)


class ArtifactComparisonFactory:
    def __init__(
        self,
        evidence_metric_delta_builder: (
            EvidenceMetricDeltaBuilder | None
        ) = None,
    ) -> None:
        self.evidence_metric_delta_builder = (
            evidence_metric_delta_builder
            or EvidenceMetricDeltaBuilder()
        )

    def create(
        self,
        artifact_a_id: str,
        artifact_b_id: str,
        previous_hypothesis: str | None,
        current_hypothesis: str,
        hypothesis_change_reason: str | None,
        previous_evidence: dict[str, Any] | None,
        current_evidence: dict[str, Any],
        evidence_change_reason: str | None,
        previous_confidence: float,
        current_confidence: float,
        confidence_change_reason: str | None,
    ) -> ArtifactComparison:
        hypothesis_evolution = HypothesisEvolution(
            previous_hypothesis=previous_hypothesis,
            current_hypothesis=current_hypothesis,
            change_reason=hypothesis_change_reason,
        )

        metric_deltas = (
            self.evidence_metric_delta_builder.build(
                previous_evidence=previous_evidence,
                current_evidence=current_evidence,
            )
        )

        evidence_evolution = EvidenceEvolution(
            previous_evidence=previous_evidence,
            current_evidence=current_evidence,
            metric_deltas=metric_deltas,
            change_reason=evidence_change_reason,
        )

        confidence_evolution = ConfidenceEvolution(
            previous_confidence=previous_confidence,
            current_confidence=current_confidence,
            change_reason=confidence_change_reason,
        )

        return ArtifactComparison(
            artifact_a_id=artifact_a_id,
            artifact_b_id=artifact_b_id,
            hypothesis_evolution=hypothesis_evolution,
            evidence_evolution=evidence_evolution,
            confidence_evolution=confidence_evolution,
        )