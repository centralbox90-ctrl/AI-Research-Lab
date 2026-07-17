from typing import Any


class ArtifactComparisonInputExtractor:
    """
    Extracts comparison input from two serialized research artifacts.

    Expected artifact structure:

    {
        "metadata": {
            "artifact_id": str
        },
        "specification": {
            "hypothesis_title": str,
            "hypothesis_description": str
        },
        "cycle": {
            "evidence": {
                "data": dict
            },
            "evidence_strength_evaluation": {
                "score": float
            }
        }
    }
    """

    def extract(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "artifact_a_id": self._extract_artifact_id(
                artifact_a,
            ),
            "artifact_b_id": self._extract_artifact_id(
                artifact_b,
            ),
            "previous_hypothesis": self._extract_hypothesis(
                artifact_a,
            ),
            "current_hypothesis": self._extract_hypothesis(
                artifact_b,
            ),
            "hypothesis_change_reason": (
                self._build_hypothesis_change_reason(
                    artifact_a,
                    artifact_b,
                )
            ),
            "previous_evidence": self._extract_evidence(
                artifact_a,
            ),
            "current_evidence": self._extract_evidence(
                artifact_b,
            ),
            "evidence_change_reason": (
                self._build_evidence_change_reason(
                    artifact_a,
                    artifact_b,
                )
            ),
            "previous_confidence": self._extract_confidence(
                artifact_a,
            ),
            "current_confidence": self._extract_confidence(
                artifact_b,
            ),
            "confidence_change_reason": (
                self._build_confidence_change_reason(
                    artifact_a,
                    artifact_b,
                )
            ),
        }

    def _extract_artifact_id(
        self,
        artifact: dict[str, Any],
    ) -> str:
        metadata = artifact.get("metadata")

        if not isinstance(metadata, dict):
            raise ValueError(
                "Research artifact metadata must be a dictionary."
            )

        artifact_id = metadata.get("artifact_id")

        if not isinstance(artifact_id, str) or not artifact_id:
            raise ValueError(
                "Research artifact metadata must contain artifact_id."
            )

        return artifact_id

    def _extract_hypothesis(
        self,
        artifact: dict[str, Any],
    ) -> str:
        specification = artifact.get("specification")

        if not isinstance(specification, dict):
            raise ValueError(
                "Research artifact specification must be a dictionary."
            )

        title = specification.get("hypothesis_title")
        description = specification.get(
            "hypothesis_description"
        )

        if isinstance(description, str) and description:
            return description

        if isinstance(title, str) and title:
            return title

        raise ValueError(
            "Research artifact specification must contain "
            "a hypothesis."
        )

    def _extract_evidence(
        self,
        artifact: dict[str, Any],
    ) -> dict[str, Any]:
        cycle = artifact.get("cycle")

        if not isinstance(cycle, dict):
            raise ValueError(
                "Research artifact cycle must be a dictionary."
            )

        evidence = cycle.get("evidence")

        if not isinstance(evidence, dict):
            raise ValueError(
                "Research artifact cycle must contain "
                "evidence as a dictionary."
            )

        evidence_data = evidence.get("data")

        if not isinstance(evidence_data, dict):
            raise ValueError(
                "Research artifact evidence must contain "
                "data as a dictionary."
            )

        return dict(evidence_data)

    def _extract_confidence(
        self,
        artifact: dict[str, Any],
    ) -> float:
        cycle = artifact.get("cycle")

        if not isinstance(cycle, dict):
            raise ValueError(
                "Research artifact cycle must be a dictionary."
            )

        evaluation = cycle.get(
            "evidence_strength_evaluation"
        )

        if not isinstance(evaluation, dict):
            raise ValueError(
                "Research artifact cycle must contain "
                "evidence_strength_evaluation."
            )

        confidence = evaluation.get("score")

        if not isinstance(confidence, (int, float)):
            raise ValueError(
                "Evidence strength evaluation must contain "
                "a numeric score."
            )

        return float(confidence)

    def _build_hypothesis_change_reason(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> str | None:
        previous = self._extract_hypothesis(
            artifact_a,
        )
        current = self._extract_hypothesis(
            artifact_b,
        )

        if previous == current:
            return None

        return (
            "Hypothesis changed between research artifacts."
        )

    def _build_evidence_change_reason(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> str | None:
        previous = self._extract_evidence(
            artifact_a,
        )
        current = self._extract_evidence(
            artifact_b,
        )

        if previous == current:
            return None

        return "Evidence changed between research artifacts."

    def _build_confidence_change_reason(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> str | None:
        previous = self._extract_confidence(
            artifact_a,
        )
        current = self._extract_confidence(
            artifact_b,
        )

        if previous == current:
            return None

        if current > previous:
            return "Confidence increased."

        return "Confidence decreased."