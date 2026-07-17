import json

from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)


class CompareResearchArtifactsCommand:
    """
    CLI command for comparing two stored research artifacts.
    """

    def __init__(
        self,
        compare_stored_research_artifacts: (
            CompareStoredResearchArtifacts
        ),
    ) -> None:
        self.compare_stored_research_artifacts = (
            compare_stored_research_artifacts
        )

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
        *,
        indent: int | None = 2,
    ) -> str:
        comparison = (
            self.compare_stored_research_artifacts.execute(
                artifact_a_result_id=artifact_a_result_id,
                artifact_b_result_id=artifact_b_result_id,
            )
        )

        return json.dumps(
            {
                "artifact_a_id": comparison.artifact_a_id,
                "artifact_b_id": comparison.artifact_b_id,
                "hypothesis_evolution": {
                    "previous_hypothesis": (
                        comparison
                        .hypothesis_evolution
                        .previous_hypothesis
                    ),
                    "current_hypothesis": (
                        comparison
                        .hypothesis_evolution
                        .current_hypothesis
                    ),
                    "change_reason": (
                        comparison
                        .hypothesis_evolution
                        .change_reason
                    ),
                },
                "evidence_evolution": {
                    "previous_evidence": (
                        comparison
                        .evidence_evolution
                        .previous_evidence
                    ),
                    "current_evidence": (
                        comparison
                        .evidence_evolution
                        .current_evidence
                    ),
                    "metric_deltas": [
                        {
                            "metric_name": delta.metric_name,
                            "previous_value": (
                                delta.previous_value
                            ),
                            "current_value": (
                                delta.current_value
                            ),
                            "absolute_delta": (
                                delta.absolute_delta
                            ),
                            "direction": delta.direction,
                        }
                        for delta in (
                            comparison
                            .evidence_evolution
                            .metric_deltas
                        )
                    ],
                    "change_reason": (
                        comparison
                        .evidence_evolution
                        .change_reason
                    ),
                },
                "confidence_evolution": {
                    "previous_confidence": (
                        comparison
                        .confidence_evolution
                        .previous_confidence
                    ),
                    "current_confidence": (
                        comparison
                        .confidence_evolution
                        .current_confidence
                    ),
                    "change_reason": (
                        comparison
                        .confidence_evolution
                        .change_reason
                    ),
                },
            },
            indent=indent,
            sort_keys=True,
        )