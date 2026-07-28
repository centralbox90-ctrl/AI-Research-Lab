from __future__ import annotations

import pytest

from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_promotion_policy import (
    KnowledgePromotionPolicy,
)


def _evaluation(
    *,
    state: HypothesisEvaluationState = (
        HypothesisEvaluationState.SUPPORTED
    ),
    confidence: float = 0.75,
    finding_refs: tuple[str, ...] = (
        "finding-1",
        "finding-2",
    ),
) -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id="evaluation-1",
        hypothesis_id="hypothesis-1",
        state=state,
        confidence=confidence,
        finding_refs=finding_refs,
        rationale=("evaluation rationale",),
        provenance=(("producer", "test"),),
    )


def _policy() -> KnowledgePromotionPolicy:
    return KnowledgePromotionPolicy(
        allowed_states=(
            HypothesisEvaluationState.SUPPORTED,
        ),
        minimum_confidence=0.75,
        minimum_findings=2,
    )


def test_policy_allows_evaluation_at_boundaries():
    policy = _policy()
    evaluation = _evaluation()

    assert policy.allows(
        evaluation=evaluation
    )
    assert policy.rejection_reasons(
        evaluation=evaluation
    ) == ()


def test_policy_rejects_disallowed_state():
    policy = _policy()
    evaluation = _evaluation(
        state=(
            HypothesisEvaluationState
            .PARTIALLY_SUPPORTED
        ),
        confidence=1.0,
    )

    assert not policy.allows(
        evaluation=evaluation
    )
    assert policy.rejection_reasons(
        evaluation=evaluation
    ) == (
        "state must be one of: supported",
    )


def test_policy_reports_all_threshold_failures():
    policy = _policy()
    evaluation = _evaluation(
        confidence=0.5,
        finding_refs=("finding-1",),
    )

    assert policy.rejection_reasons(
        evaluation=evaluation
    ) == (
        "confidence must be at least 0.75",
        "finding_refs must contain at least 2 items",
    )


def test_policy_requires_hypothesis_evaluation():
    policy = _policy()

    with pytest.raises(
        TypeError,
        match=(
            "evaluation must be a "
            "HypothesisEvaluation"
        ),
    ):
        policy.allows(
            evaluation=object(),
        )


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    (
        ("allowed_states", [], TypeError),
        ("allowed_states", (), ValueError),
        (
            "allowed_states",
            ("supported",),
            TypeError,
        ),
        (
            "allowed_states",
            (
                HypothesisEvaluationState.SUPPORTED,
                HypothesisEvaluationState.SUPPORTED,
            ),
            ValueError,
        ),
        ("minimum_confidence", True, TypeError),
        ("minimum_confidence", -0.1, ValueError),
        ("minimum_confidence", 1.1, ValueError),
        ("minimum_findings", True, TypeError),
        ("minimum_findings", 0, ValueError),
    ),
)
def test_policy_validates_configuration(
    field: str,
    value: object,
    error_type: type[Exception],
):
    arguments = {
        "allowed_states": (
            HypothesisEvaluationState.SUPPORTED,
        ),
        "minimum_confidence": 0.75,
        "minimum_findings": 2,
    }
    arguments[field] = value

    with pytest.raises(error_type):
        KnowledgePromotionPolicy(**arguments)
