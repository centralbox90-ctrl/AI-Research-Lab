from datetime import UTC, datetime

import pandas as pd
import pytest

from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_analysis_service import (
    ComparativeAnalysisService,
)
from src.research.comparative_statistical_evaluator import (
    ComparativeStatisticalEvaluator,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "close": [
                100.0,
                101.0,
                99.0,
                102.0,
                100.0,
                104.0,
                103.0,
                106.0,
                105.0,
                108.0,
                107.0,
                110.0,
            ],
        }
    )


def build_observation(
    observation_id: str,
    bar_index: int,
) -> Observation:
    data = build_data()

    return Observation(
        id=observation_id,
        definition_id="rsi-level-cross",
        symbol="EURUSD",
        timeframe="H1",
        timestamp=datetime(
            2026,
            1,
            1,
            hour=bar_index,
            tzinfo=UTC,
        ),
        bar_index=bar_index,
        price=float(
            data.iloc[bar_index]["close"]
        ),
    )


def build_analysis() -> ComparativeAnalysis:
    return ComparativeAnalysisService().run(
        data=build_data(),
        observations=(
            build_observation("candidate-1", 1),
            build_observation("candidate-2", 4),
            build_observation("candidate-3", 7),
        ),
        specification=ForwardReturnSpecification(
            horizons=(1, 2),
        ),
    )


def evaluate(
    *,
    analysis: ComparativeAnalysis | None = None,
    confidence_level: object = 0.95,
    resample_count: object = 200,
    block_length: object = 2,
    random_seed: object = 17,
    minimum_candidate_sample_size: object = 30,
    method: object = "moving_block_bootstrap",
    research_fingerprint: object = "research-id",
    dataset_id: object = "dataset-id",
):
    plan = ComparativeEvaluationPlan(
        method=method,  # type: ignore[arg-type]
        confidence_level=confidence_level,
        resample_count=resample_count,
        block_length=block_length,
        random_seed=random_seed,
        minimum_candidate_sample_size=(
            minimum_candidate_sample_size
        ),
    )

    return ComparativeStatisticalEvaluator().evaluate(
        analysis=(
            analysis
            if analysis is not None
            else build_analysis()
        ),
        research_fingerprint=research_fingerprint,
        dataset_id=dataset_id,
        plan=plan,
    )

def test_evaluates_each_comparison_horizon(
) -> None:
    analysis = build_analysis()
    evaluations = evaluate(
        analysis=analysis,
        research_fingerprint="  research-id  ",
        dataset_id="  dataset-id  ",
    )

    assert tuple(
        evaluation.horizon
        for evaluation in evaluations
    ) == (1, 2)

    comparison_by_horizon = {
        comparison.horizon: comparison
        for comparison in analysis.comparisons
    }

    for evaluation in evaluations:
        comparison = comparison_by_horizon[
            evaluation.horizon
        ]

        assert evaluation.research_fingerprint == (
            "research-id"
        )
        assert evaluation.dataset_id == "dataset-id"
        assert evaluation.candidate_sample_size == (
            comparison.candidate_sample_size
        )
        assert evaluation.baseline_sample_size == (
            comparison.baseline_sample_size
        )
        assert evaluation.effect_estimate == (
            pytest.approx(
                comparison.mean_return_difference
            )
        )
        assert evaluation.confidence_level == 0.95
        assert evaluation.method == (
            "moving_block_bootstrap"
        )
        assert evaluation.resample_count == 200
        assert evaluation.block_length == 2
        assert evaluation.random_seed == 17
        assert (
            "candidate sample size is below 30"
            in evaluation.warnings
        )


def test_is_deterministic_for_same_seed(
) -> None:
    first = evaluate()
    second = evaluate()

    assert first == second


def test_different_seed_changes_interval(
) -> None:
    first = evaluate(
        random_seed=17,
    )
    second = evaluate(
        random_seed=18,
    )

    first_intervals = tuple(
        (
            evaluation.confidence_interval_lower,
            evaluation.confidence_interval_upper,
        )
        for evaluation in first
    )
    second_intervals = tuple(
        (
            evaluation.confidence_interval_lower,
            evaluation.confidence_interval_upper,
        )
        for evaluation in second
    )

    assert first_intervals != second_intervals


def test_horizon_results_do_not_depend_on_order(
) -> None:
    analysis = build_analysis()
    reversed_analysis = ComparativeAnalysis(
        candidate_result=analysis.candidate_result,
        baseline_result=analysis.baseline_result,
        candidate_statistics=tuple(
            reversed(
                analysis.candidate_statistics
            )
        ),
        baseline_statistics=tuple(
            reversed(
                analysis.baseline_statistics
            )
        ),
        comparisons=tuple(
            reversed(analysis.comparisons)
        ),
    )

    original_by_horizon = {
        evaluation.horizon: evaluation
        for evaluation in evaluate(
            analysis=analysis
        )
    }
    reversed_by_horizon = {
        evaluation.horizon: evaluation
        for evaluation in evaluate(
            analysis=reversed_analysis
        )
    }

    assert original_by_horizon == (
        reversed_by_horizon
    )


def test_full_length_block_preserves_effect(
) -> None:
    analysis = build_analysis()
    baseline_sample_size = (
        analysis.comparisons[0]
        .baseline_sample_size
    )
    evaluations = evaluate(
        analysis=analysis,
        resample_count=20,
        block_length=baseline_sample_size,
    )

    comparison_by_horizon = {
        comparison.horizon: comparison
        for comparison in analysis.comparisons
    }

    for evaluation in evaluations:
        expected_effect = (
            comparison_by_horizon[
                evaluation.horizon
            ].mean_return_difference
        )

        assert (
            evaluation.confidence_interval_lower
            == pytest.approx(expected_effect)
        )
        assert (
            evaluation.confidence_interval_upper
            == pytest.approx(expected_effect)
        )


def test_does_not_modify_analysis(
) -> None:
    analysis = build_analysis()
    original = analysis

    evaluate(
        analysis=analysis,
    )

    assert analysis == original


def test_rejects_invalid_analysis() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analysis must be a "
            "ComparativeAnalysis"
        ),
    ):
        ComparativeStatisticalEvaluator().evaluate(
            analysis=object(),
            research_fingerprint="research-id",
            dataset_id="dataset-id",
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "error_type",
        "message",
    ),
    [
        (
            "research_fingerprint",
            None,
            TypeError,
            "research_fingerprint must be a string",
        ),
        (
            "research_fingerprint",
            " ",
            ValueError,
            "research_fingerprint must not be empty",
        ),
        (
            "dataset_id",
            None,
            TypeError,
            "dataset_id must be a string",
        ),
        (
            "dataset_id",
            " ",
            ValueError,
            "dataset_id must not be empty",
        ),
    ],
)
def test_rejects_invalid_identity(
    field_name: str,
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            **{field_name: value},
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "confidence_level must be a real number",
        ),
        (
            float("nan"),
            ValueError,
            "confidence_level must be finite",
        ),
        (
            float("inf"),
            ValueError,
            "confidence_level must be finite",
        ),
        (
            0.0,
            ValueError,
            "confidence_level must be between 0 and 1",
        ),
        (
            1.0,
            ValueError,
            "confidence_level must be between 0 and 1",
        ),
    ],
)
def test_rejects_invalid_confidence_level(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            confidence_level=value,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "resample_count must be an integer",
        ),
        (
            0,
            ValueError,
            "resample_count must be positive",
        ),
        (
            1,
            ValueError,
            "resample_count must be at least 2",
        ),
    ],
)
def test_rejects_invalid_resample_count(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            resample_count=value,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "block_length must be an integer",
        ),
        (
            0,
            ValueError,
            "block_length must be positive",
        ),
    ],
)
def test_rejects_invalid_block_length(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            block_length=value,
        )


def test_rejects_block_larger_than_baseline(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "block_length must not exceed "
            "the baseline sample size"
        ),
    ):
        evaluate(
            block_length=11,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "random_seed must be an integer",
        ),
        (
            -1,
            ValueError,
            "random_seed must not be negative",
        ),
    ],
)
def test_rejects_invalid_random_seed(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        evaluate(
            random_seed=value,
        )

def test_rejects_invalid_plan() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "plan must be a "
            "ComparativeEvaluationPlan"
        ),
    ):
        ComparativeStatisticalEvaluator().evaluate(
            analysis=build_analysis(),
            research_fingerprint="research-id",
            dataset_id="dataset-id",
            plan=object(),
        )


def test_rejects_unsupported_plan_method(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "unsupported comparative evaluation "
            "method: unsupported"
        ),
    ):
        evaluate(
            method="unsupported",
        )


def test_uses_plan_sample_warning_threshold(
) -> None:
    evaluations = evaluate(
        minimum_candidate_sample_size=3,
    )

    for evaluation in evaluations:
        assert (
            "candidate sample size is below 30"
            not in evaluation.warnings
        )
