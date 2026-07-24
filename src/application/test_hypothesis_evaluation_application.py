import pytest

from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.research.finding import (
    Finding,
    FindingRelationship,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)
from src.research.hypothesis_evaluator import (
    HypothesisEvaluator,
)


def build_finding() -> Finding:
    return Finding(
        id="finding-a",
        hypothesis_id="hypothesis-rsi",
        statement="RSI finding.",
        relationship=FindingRelationship.SUPPORTING,
        confidence=0.8,
        applicable_markets=(
            "EURUSD:H1",
        ),
        limitations=(),
        supporting_evidence=(
            "evidence-a",
        ),
        provenance=(
            (
                "finding_pipeline_version",
                "finding-v2",
            ),
        ),
    )


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id="hypothesis-evaluation-id",
        hypothesis_id="hypothesis-rsi",
        state=(
            HypothesisEvaluationState
            .PARTIALLY_SUPPORTED
        ),
        confidence=0.8,
        finding_refs=(
            "finding-a",
        ),
        rationale=(
            "partial support",
        ),
        limitations=(
            "only one finding",
        ),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )


class StubHypothesisEvaluator(
    HypothesisEvaluator
):
    def __init__(
        self,
        result: HypothesisEvaluation,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[Finding, ...]
        ] = []

    def evaluate(
        self,
        *,
        findings: tuple[Finding, ...],
    ) -> HypothesisEvaluation:
        self.calls.append(findings)

        return self.result


def test_delegates_findings_to_domain_evaluator(
) -> None:
    expected = build_evaluation()
    evaluator = StubHypothesisEvaluator(
        expected
    )
    application = HypothesisEvaluationApplication(
        hypothesis_evaluator=evaluator,
    )
    findings = (
        build_finding(),
    )

    result = application.run(
        findings=findings,
    )

    assert result is expected
    assert evaluator.calls == [findings]


def test_rejects_invalid_evaluator() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "hypothesis_evaluator must be a "
            "HypothesisEvaluator"
        ),
    ):
        HypothesisEvaluationApplication(
            hypothesis_evaluator=object(),  # type: ignore[arg-type]
        )


def test_preserves_domain_validation() -> None:
    evaluator = HypothesisEvaluator(
        plan=HypothesisEvaluationPlan(),
    )
    application = HypothesisEvaluationApplication(
        hypothesis_evaluator=evaluator,
    )

    with pytest.raises(
        ValueError,
        match="findings must not be empty",
    ):
        application.run(findings=())