import json

import pytest

from src.cli.hypothesis_evaluation_presenter import (
    present_hypothesis_evaluation,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:example"
        ),
        hypothesis_id="hypothesis-rsi",
        state=(
            HypothesisEvaluationState
            .PARTIALLY_SUPPORTED
        ),
        confidence=0.8,
        finding_refs=(
            "finding-b",
            "finding-a",
        ),
        rationale=(
            "findings provide partial support",
        ),
        limitations=(
            "mixed market conditions",
        ),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
            (
                "evaluation_plan_fingerprint",
                "plan-fingerprint",
            ),
        ),
    )


def test_presents_json_compatible_evaluation(
) -> None:
    evaluation = build_evaluation()
    payload = present_hypothesis_evaluation(
        evaluation
    )
    serialized = json.loads(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )

    assert serialized["artifact_type"] == (
        "hypothesis_evaluation"
    )
    assert serialized["artifact_version"] == 1

    presented = serialized["evaluation"]

    assert presented["schema_version"] == 1
    assert presented["id"] == (
        "hypothesis-evaluation:"
        "sha256:example"
    )
    assert presented["fingerprint"] == (
        evaluation.fingerprint
    )
    assert presented["hypothesis_id"] == (
        "hypothesis-rsi"
    )
    assert presented["state"] == (
        "partially_supported"
    )
    assert presented["confidence"] == 0.8
    assert presented["finding_refs"] == [
        "finding-a",
        "finding-b",
    ]
    assert presented["rationale"] == [
        "findings provide partial support",
    ]
    assert presented["limitations"] == [
        "mixed market conditions",
    ]
    assert presented["provenance"] == {
        "evaluation_plan_fingerprint": (
            "plan-fingerprint"
        ),
        "evaluation_plan_version": (
            "hypothesis-evaluation-v1"
        ),
    }


def test_rejects_invalid_evaluation() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "evaluation must be a "
            "HypothesisEvaluation"
        ),
    ):
        present_hypothesis_evaluation(
            object()
        )