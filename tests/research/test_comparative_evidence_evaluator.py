import pytest

from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
    ExpectedEffectDirection,
)
from src.research.comparative_evidence_evaluator import (
    ComparativeEvidenceEvaluator,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.evidence import (
    EvidenceDirection,
    EvidenceStrength,
)


def build_evaluation(
    dataset_id: str,
    **overrides: object,
) -> ComparativeStatisticalEvaluation:
    arguments: dict[str, object] = {
        "research_fingerprint": "research-id",
        "dataset_id": dataset_id,
        "horizon": 3,
        "candidate_sample_size": 100,
        "baseline_sample_size": 500,
        "effect_estimate": 0.002,
        "confidence_interval_lower": 0.001,
        "confidence_interval_upper": 0.003,
        "confidence_level": 0.95,
        "method": "moving_block_bootstrap",
        "resample_count": 2_000,
        "block_length": 24,
        "random_seed": 0,
        "warnings": (),
    }
    arguments.update(overrides)

    return ComparativeStatisticalEvaluation(
        **arguments,  # type: ignore[arg-type]
    )


def evaluate(
    evaluations: object,
    *,
    plan: object | None = None,
    **overrides: object,
):
    arguments: dict[str, object] = {
        "hypothesis_id": "  hypothesis-rsi  ",
        "indicator_id": "  rsi  ",
        "symbol": " eurusd ",
        "timeframe": " h1 ",
        "evaluations": evaluations,
        "plan": (
            ComparativeEvaluationPlan()
            if plan is None
            else plan
        ),
    }
    arguments.update(overrides)

    return ComparativeEvidenceEvaluator().evaluate(
        **arguments,  # type: ignore[arg-type]
    )


def test_builds_strong_supporting_evidence(
) -> None:
    evidence = evaluate(
        (
            build_evaluation("dataset-b"),
            build_evaluation("dataset-a"),
        )
    )

    assert evidence.id.startswith(
        "evidence:sha256:"
    )
    assert evidence.hypothesis_id == (
        "hypothesis-rsi"
    )
    assert evidence.observation_refs == (
        "dataset-a:horizon:3",
        "dataset-b:horizon:3",
    )
    assert evidence.direction is (
        EvidenceDirection.SUPPORTING
    )
    assert evidence.strength is (
        EvidenceStrength.STRONG
    )
    assert evidence.confidence == pytest.approx(
        0.95
    )
    assert evidence.consistency == 1.0
    assert evidence.robustness == 1.0
    assert evidence.applicability == (
        "indicator:rsi",
        "symbol:EURUSD",
        "timeframe:H1",
        "horizon:3",
    )
    assert evidence.limitations == ()

    provenance = dict(evidence.provenance)

    assert provenance[
        "research_fingerprint"
    ] == "research-id"
    assert provenance[
        "evaluation_plan_fingerprint"
    ] == ComparativeEvaluationPlan().fingerprint
    assert provenance["horizon"] == "3"
    assert provenance[
        "replication_count"
    ] == "2"
    assert provenance[
        "eligible_replication_count"
    ] == "2"
    assert provenance[
        "supporting_replication_count"
    ] == "2"
    assert provenance[
        "contradictory_replication_count"
    ] == "0"
    assert provenance["dataset_ids"] == (
        '["dataset-a","dataset-b"]'
    )


def test_is_deterministic_and_order_independent(
) -> None:
    first = build_evaluation("dataset-a")
    second = build_evaluation("dataset-b")

    original = evaluate(
        (
            first,
            second,
        )
    )
    reversed_result = evaluate(
        (
            second,
            first,
        )
    )

    assert original == reversed_result
    assert original.fingerprint == (
        reversed_result.fingerprint
    )


def test_requires_predeclared_supporting_replications(
) -> None:
    evidence = evaluate(
        (
            build_evaluation("dataset-a"),
            build_evaluation(
                "dataset-b",
                confidence_interval_lower=-0.001,
                confidence_interval_upper=0.003,
            ),
        )
    )

    assert evidence.direction is (
        EvidenceDirection.INCONCLUSIVE
    )
    assert evidence.strength is (
        EvidenceStrength.WEAK
    )
    assert evidence.confidence == pytest.approx(
        0.475
    )
    assert evidence.consistency == 1.0
    assert (
        "supporting replication count is below 2"
        in evidence.limitations
    )
    assert (
        "1 eligible replication(s) have "
        "confidence intervals including zero"
        in evidence.limitations
    )


def test_detects_contradictory_replication(
) -> None:
    evidence = evaluate(
        (
            build_evaluation(
                "dataset-a",
                effect_estimate=-0.002,
                confidence_interval_lower=-0.003,
                confidence_interval_upper=-0.001,
            ),
            build_evaluation(
                "dataset-b",
                effect_estimate=0.001,
                confidence_interval_lower=-0.001,
                confidence_interval_upper=0.003,
            ),
        )
    )

    assert evidence.direction is (
        EvidenceDirection.CONTRADICTORY
    )
    assert evidence.strength is (
        EvidenceStrength.MODERATE
    )
    assert evidence.confidence == pytest.approx(
        0.475
    )
    assert evidence.consistency == 0.5
    assert (
        "1 statistically significant "
        "contradictory replication(s)"
        in evidence.limitations
    )


@pytest.mark.parametrize(
    (
        "expected_direction",
        "first_interval",
        "second_interval",
    ),
    (
        (
            ExpectedEffectDirection.NEGATIVE,
            (-0.003, -0.001),
            (-0.004, -0.002),
        ),
        (
            ExpectedEffectDirection.TWO_SIDED,
            (0.001, 0.003),
            (-0.004, -0.002),
        ),
    ),
)
def test_supports_predeclared_effect_direction(
    expected_direction: ExpectedEffectDirection,
    first_interval: tuple[float, float],
    second_interval: tuple[float, float],
) -> None:
    first_effect = sum(first_interval) / 2.0
    second_effect = sum(second_interval) / 2.0
    plan = ComparativeEvaluationPlan(
        expected_direction=expected_direction,
    )

    evidence = evaluate(
        (
            build_evaluation(
                "dataset-a",
                effect_estimate=first_effect,
                confidence_interval_lower=(
                    first_interval[0]
                ),
                confidence_interval_upper=(
                    first_interval[1]
                ),
            ),
            build_evaluation(
                "dataset-b",
                effect_estimate=second_effect,
                confidence_interval_lower=(
                    second_interval[0]
                ),
                confidence_interval_upper=(
                    second_interval[1]
                ),
            ),
        ),
        plan=plan,
    )

    assert evidence.direction is (
        EvidenceDirection.SUPPORTING
    )
    assert evidence.strength is (
        EvidenceStrength.STRONG
    )


def test_excludes_replication_below_sample_threshold(
) -> None:
    evidence = evaluate(
        (
            build_evaluation("dataset-a"),
            build_evaluation(
                "dataset-b",
                candidate_sample_size=10,
            ),
        )
    )

    assert evidence.direction is (
        EvidenceDirection.INCONCLUSIVE
    )
    assert evidence.strength is (
        EvidenceStrength.WEAK
    )
    assert evidence.robustness == 0.5
    assert (
        "eligible replication count is below 2"
        in evidence.limitations
    )
    assert (
        "1 replication(s) are below the "
        "minimum candidate sample size"
        in evidence.limitations
    )


def test_preserves_statistical_warnings_as_limitations(
) -> None:
    evidence = evaluate(
        (
            build_evaluation(
                "dataset-a",
                warnings=(
                    "candidate sample is sparse",
                ),
            ),
            build_evaluation("dataset-b"),
        )
    )

    assert (
        "dataset-a: candidate sample is sparse"
        in evidence.limitations
    )


@pytest.mark.parametrize(
    (
        "evaluations",
        "error_type",
        "message",
    ),
    (
        (
            [],
            TypeError,
            "evaluations must be a tuple",
        ),
        (
            (),
            ValueError,
            "evaluations must not be empty",
        ),
        (
            (object(),),
            TypeError,
            "each evaluation must be a "
            "ComparativeStatisticalEvaluation",
        ),
    ),
)
def test_rejects_invalid_evaluation_collection(
    evaluations: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(evaluations)


def test_rejects_mixed_research_fingerprints(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "evaluations must use the same "
            "research fingerprint"
        ),
    ):
        evaluate(
            (
                build_evaluation("dataset-a"),
                build_evaluation(
                    "dataset-b",
                    research_fingerprint=(
                        "different-research"
                    ),
                ),
            )
        )


def test_rejects_mixed_horizons() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "evaluations must use the same horizon"
        ),
    ):
        evaluate(
            (
                build_evaluation("dataset-a"),
                build_evaluation(
                    "dataset-b",
                    horizon=5,
                ),
            )
        )


def test_rejects_duplicate_dataset() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "evaluations must use distinct datasets"
        ),
    ):
        evaluate(
            (
                build_evaluation("dataset-a"),
                build_evaluation("dataset-a"),
            )
        )


@pytest.mark.parametrize(
    (
        "evaluation_overrides",
        "message",
    ),
    (
        (
            {
                "method": "stationary_bootstrap",
            },
            "evaluation method must match the plan",
        ),
        (
            {
                "confidence_level": 0.9,
            },
            "evaluation confidence level must "
            "match the plan",
        ),
        (
            {
                "resample_count": 100,
            },
            "evaluation resample count must "
            "match the plan",
        ),
        (
            {
                "block_length": 12,
            },
            "evaluation block length must "
            "match the plan",
        ),
        (
            {
                "random_seed": 17,
            },
            "evaluation random seed must "
            "match the plan",
        ),
    ),
)
def test_rejects_evaluation_plan_mismatch(
    evaluation_overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        evaluate(
            (
                build_evaluation(
                    "dataset-a",
                    **evaluation_overrides,
                ),
            )
        )


def test_rejects_invalid_plan() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "plan must be a "
            "ComparativeEvaluationPlan"
        ),
    ):
        evaluate(
            (
                build_evaluation("dataset-a"),
            ),
            plan=object(),
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "error_type",
        "message",
    ),
    (
        (
            "hypothesis_id",
            None,
            TypeError,
            "hypothesis_id must be a string",
        ),
        (
            "indicator_id",
            "   ",
            ValueError,
            "indicator_id must not be empty",
        ),
        (
            "symbol",
            "   ",
            ValueError,
            "symbol must not be empty",
        ),
        (
            "timeframe",
            object(),
            TypeError,
            "timeframe must be a string",
        ),
    ),
)
def test_rejects_invalid_identity(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            (
                build_evaluation("dataset-a"),
            ),
            **{field_name: invalid_value},
        )
