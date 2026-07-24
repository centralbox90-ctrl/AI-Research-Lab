import pytest

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


def build_finding(
    *,
    finding_id: str,
    relationship: FindingRelationship,
    confidence: float,
    hypothesis_id: str = "hypothesis-rsi",
    limitations: tuple[str, ...] = (),
) -> Finding:
    return Finding(
        id=finding_id,
        hypothesis_id=hypothesis_id,
        statement=f"Finding {finding_id}.",
        relationship=relationship,
        confidence=confidence,
        applicable_markets=(
            "EURUSD:H1",
        ),
        limitations=limitations,
        supporting_evidence=(
            f"evidence-{finding_id}",
        ),
        provenance=(
            (
                "finding_pipeline_version",
                "finding-v2",
            ),
        ),
    )


def build_evaluator(
    **plan_overrides: object,
) -> HypothesisEvaluator:
    plan_values: dict[str, object] = {
        "version": "hypothesis-evaluation-v1",
        "supported_confidence_threshold": 0.75,
        "partially_supported_confidence_threshold": (
            0.5
        ),
        "rejected_confidence_threshold": 0.75,
        "minimum_decisive_findings": 2,
    }
    plan_values.update(plan_overrides)

    plan = HypothesisEvaluationPlan(
        **plan_values
    )  # type: ignore[arg-type]

    return HypothesisEvaluator(plan=plan)


def test_evaluates_supported_hypothesis() -> None:
    evaluation = build_evaluator().evaluate(
        findings=(
            build_finding(
                finding_id="finding-b",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.9,
            ),
            build_finding(
                finding_id="finding-a",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.8,
            ),
        ),
    )

    assert isinstance(
        evaluation,
        HypothesisEvaluation,
    )
    assert evaluation.id.startswith(
        "hypothesis-evaluation:sha256:"
    )
    assert evaluation.hypothesis_id == (
        "hypothesis-rsi"
    )
    assert evaluation.state is (
        HypothesisEvaluationState.SUPPORTED
    )
    assert evaluation.confidence == pytest.approx(
        0.85
    )
    assert evaluation.finding_refs == (
        "finding-a",
        "finding-b",
    )
    assert evaluation.rationale == (
        "all findings support the hypothesis "
        "under the decisive plan rules",
    )

    provenance = dict(evaluation.provenance)

    assert provenance[
        "evaluation_plan_version"
    ] == "hypothesis-evaluation-v1"
    assert len(
        provenance["evaluation_plan_fingerprint"]
    ) == 64


def test_evaluates_rejected_hypothesis() -> None:
    evaluation = build_evaluator().evaluate(
        findings=(
            build_finding(
                finding_id="finding-a",
                relationship=(
                    FindingRelationship.CONTRADICTORY
                ),
                confidence=0.8,
            ),
            build_finding(
                finding_id="finding-b",
                relationship=(
                    FindingRelationship.CONTRADICTORY
                ),
                confidence=0.9,
            ),
        ),
    )

    assert evaluation.state is (
        HypothesisEvaluationState.REJECTED
    )


def test_single_supporting_finding_is_partial(
) -> None:
    evaluation = build_evaluator().evaluate(
        findings=(
            build_finding(
                finding_id="finding-a",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.9,
            ),
        ),
    )

    assert evaluation.state is (
        HypothesisEvaluationState
        .PARTIALLY_SUPPORTED
    )
    assert evaluation.limitations == (
        "only 1 findings available; "
        "2 required for a decisive state",
    )


def test_mixed_findings_are_partial() -> None:
    evaluation = build_evaluator().evaluate(
        findings=(
            build_finding(
                finding_id="finding-a",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.8,
            ),
            build_finding(
                finding_id="finding-b",
                relationship=(
                    FindingRelationship.CONTRADICTORY
                ),
                confidence=0.8,
            ),
        ),
    )

    assert evaluation.state is (
        HypothesisEvaluationState
        .PARTIALLY_SUPPORTED
    )
    assert (
        "findings have mixed relationships "
        "to the hypothesis"
    ) in evaluation.limitations


@pytest.mark.parametrize(
    "findings",
    (
        (
            build_finding(
                finding_id="finding-low",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.3,
            ),
        ),
        (
            build_finding(
                finding_id="finding-inconclusive",
                relationship=(
                    FindingRelationship.INCONCLUSIVE
                ),
                confidence=0.9,
            ),
        ),
    ),
)
def test_evaluates_inconclusive_hypothesis(
    findings: tuple[Finding, ...],
) -> None:
    evaluation = build_evaluator().evaluate(
        findings=findings,
    )

    assert evaluation.state is (
        HypothesisEvaluationState.INCONCLUSIVE
    )


def test_merges_finding_limitations() -> None:
    evaluation = build_evaluator().evaluate(
        findings=(
            build_finding(
                finding_id="finding-a",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.8,
                limitations=(
                    "limited history",
                ),
            ),
            build_finding(
                finding_id="finding-b",
                relationship=(
                    FindingRelationship.SUPPORTING
                ),
                confidence=0.9,
                limitations=(
                    "single asset class",
                ),
            ),
        ),
    )

    assert evaluation.limitations == (
        "limited history",
        "single asset class",
    )


def test_is_order_independent() -> None:
    first_finding = build_finding(
        finding_id="finding-a",
        relationship=FindingRelationship.SUPPORTING,
        confidence=0.8,
    )
    second_finding = build_finding(
        finding_id="finding-b",
        relationship=FindingRelationship.SUPPORTING,
        confidence=0.9,
    )

    first = build_evaluator().evaluate(
        findings=(
            first_finding,
            second_finding,
        ),
    )
    second = build_evaluator().evaluate(
        findings=(
            second_finding,
            first_finding,
        ),
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_plan_changes_result_identity() -> None:
    findings = (
        build_finding(
            finding_id="finding-a",
            relationship=FindingRelationship.SUPPORTING,
            confidence=0.8,
        ),
        build_finding(
            finding_id="finding-b",
            relationship=FindingRelationship.SUPPORTING,
            confidence=0.9,
        ),
    )

    decisive = build_evaluator().evaluate(
        findings=findings,
    )
    stricter = build_evaluator(
        minimum_decisive_findings=3,
    ).evaluate(
        findings=findings,
    )

    assert decisive.state is (
        HypothesisEvaluationState.SUPPORTED
    )
    assert stricter.state is (
        HypothesisEvaluationState
        .PARTIALLY_SUPPORTED
    )
    assert decisive.id != stricter.id


def test_rejects_invalid_plan() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "plan must be a "
            "HypothesisEvaluationPlan"
        ),
    ):
        HypothesisEvaluator(
            plan=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("findings", "error_type", "message"),
    (
        (
            [],
            TypeError,
            "findings must be a tuple",
        ),
        (
            (),
            ValueError,
            "findings must not be empty",
        ),
        (
            (object(),),
            TypeError,
            "each finding must be a Finding",
        ),
    ),
)
def test_rejects_invalid_findings(
    findings: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evaluator().evaluate(
            findings=findings,  # type: ignore[arg-type]
        )


def test_rejects_duplicate_finding_ids() -> None:
    finding = build_finding(
        finding_id="finding-a",
        relationship=FindingRelationship.SUPPORTING,
        confidence=0.8,
    )

    with pytest.raises(
        ValueError,
        match="finding ids must be unique",
    ):
        build_evaluator().evaluate(
            findings=(finding, finding),
        )


def test_rejects_different_hypotheses() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "findings must belong to "
            "the same hypothesis"
        ),
    ):
        build_evaluator().evaluate(
            findings=(
                build_finding(
                    finding_id="finding-a",
                    relationship=(
                        FindingRelationship.SUPPORTING
                    ),
                    confidence=0.8,
                    hypothesis_id="hypothesis-a",
                ),
                build_finding(
                    finding_id="finding-b",
                    relationship=(
                        FindingRelationship.SUPPORTING
                    ),
                    confidence=0.8,
                    hypothesis_id="hypothesis-b",
                ),
            ),
        )