from __future__ import annotations

from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
)


def present_hypothesis_evaluation(
    evaluation: HypothesisEvaluation,
) -> dict[str, object]:
    """Build a JSON-compatible hypothesis evaluation payload."""

    if not isinstance(
        evaluation,
        HypothesisEvaluation,
    ):
        raise TypeError(
            "evaluation must be a "
            "HypothesisEvaluation"
        )

    presented_evaluation = evaluation.to_dict()
    presented_evaluation["fingerprint"] = (
        evaluation.fingerprint
    )

    return {
        "artifact_type": "hypothesis_evaluation",
        "artifact_version": 1,
        "evaluation": presented_evaluation,
    }