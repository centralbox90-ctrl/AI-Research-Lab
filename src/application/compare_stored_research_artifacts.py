from typing import Any, Protocol

from src.application.artifact_comparison import (
    ArtifactComparison,
)
from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)


class StoredResearchArtifactGetter(Protocol):
    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        ...


class ArtifactComparisonInputExtractor(Protocol):
    def extract(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> dict[str, Any]:
        ...


class CompareStoredResearchArtifacts:
    """
    Loads two stored research artifacts and compares their
    hypothesis, evidence, and confidence evolution.

    Storage access and artifact interpretation are injected,
    keeping this use case independent from SQLite and CLI.
    """

    def __init__(
        self,
        artifact_getter: StoredResearchArtifactGetter,
        input_extractor: ArtifactComparisonInputExtractor,
        comparison_factory: (
            ArtifactComparisonFactory | None
        ) = None,
    ) -> None:
        self.artifact_getter = artifact_getter
        self.input_extractor = input_extractor
        self.comparison_factory = (
            comparison_factory
            or ArtifactComparisonFactory()
        )

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ) -> ArtifactComparison:
        artifact_a = self.artifact_getter.execute(
            artifact_a_result_id,
        )

        if artifact_a is None:
            raise ValueError(
                "Research artifact was not found for result_id: "
                f"{artifact_a_result_id}"
            )

        artifact_b = self.artifact_getter.execute(
            artifact_b_result_id,
        )

        if artifact_b is None:
            raise ValueError(
                "Research artifact was not found for result_id: "
                f"{artifact_b_result_id}"
            )

        comparison_input = self.input_extractor.extract(
            artifact_a=artifact_a,
            artifact_b=artifact_b,
        )

        return self.comparison_factory.create(
            artifact_a_id=comparison_input[
                "artifact_a_id"
            ],
            artifact_b_id=comparison_input[
                "artifact_b_id"
            ],
            previous_hypothesis=comparison_input[
                "previous_hypothesis"
            ],
            current_hypothesis=comparison_input[
                "current_hypothesis"
            ],
            hypothesis_change_reason=comparison_input[
                "hypothesis_change_reason"
            ],
            previous_evidence=comparison_input[
                "previous_evidence"
            ],
            current_evidence=comparison_input[
                "current_evidence"
            ],
            evidence_change_reason=comparison_input[
                "evidence_change_reason"
            ],
            previous_confidence=comparison_input[
                "previous_confidence"
            ],
            current_confidence=comparison_input[
                "current_confidence"
            ],
            confidence_change_reason=comparison_input[
                "confidence_change_reason"
            ],
        )