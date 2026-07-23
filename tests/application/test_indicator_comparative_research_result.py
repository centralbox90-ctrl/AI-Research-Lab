from dataclasses import FrozenInstanceError

import pytest

from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.indicators.implementations.rsi import INDICATOR
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


def build_dataset_fingerprint(
) -> MarketDatasetFingerprint:
    return MarketDatasetFingerprint(
        content_fingerprint="content-fingerprint",
        dataset_fingerprint="dataset-fingerprint",
        algorithm="sha256",
        content_schema_version="content-v1",
        dataset_schema_version="dataset-v1",
        normalization_schema_version=(
            "normalization-v1"
        ),
    )


def build_quality_report() -> DataQualityReport:
    return DataQualityReport(
        row_count=100,
        first_timestamp=1_700_000_000_000_000_000,
        last_timestamp=1_700_356_400_000_000_000,
        duplicate_timestamp_count=0,
        missing_timestamp_count=0,
        invalid_ohlc_count=0,
        monotonic_timestamp=True,
    )


def build_result(
    **overrides: object,
) -> IndicatorComparativeResearchResult:
    arguments = {
        "indicator_id": "  rsi  ",
        "symbol": " eurusd ",
        "timeframe": " h1 ",
        "research_specification": (
            create_default_research_specification(
                INDICATOR
            )
        ),
        "dataset_fingerprint": (
            build_dataset_fingerprint()
        ),
        "data_quality_report": (
            build_quality_report()
        ),
        "analysis": object.__new__(
            ComparativeAnalysis
        ),
    }
    arguments.update(overrides)

    return IndicatorComparativeResearchResult(
        **arguments
    )


def test_builds_reproducible_comparative_result(
) -> None:
    result = build_result()

    assert result.indicator_id == "rsi"
    assert result.symbol == "EURUSD"
    assert result.timeframe == "H1"
    assert result.research_fingerprint == (
        result.research_specification.fingerprint
    )
    assert result.dataset_id == "dataset-fingerprint"
    assert result.data_quality_report.row_count == 100
    assert isinstance(
        result.evaluation_plan,
        ComparativeEvaluationPlan,
    )
    assert result.evaluation_plan_fingerprint == (
        result.evaluation_plan.fingerprint
    )


def test_is_immutable() -> None:
    result = build_result()

    with pytest.raises(FrozenInstanceError):
        result.symbol = "GBPUSD"


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "error_type", "message"),
    (
        (
            "indicator_id",
            object(),
            TypeError,
            "indicator_id must be a string",
        ),
        (
            "indicator_id",
            "   ",
            ValueError,
            "indicator_id must not be empty",
        ),
        (
            "symbol",
            object(),
            TypeError,
            "symbol must be a string",
        ),
        (
            "timeframe",
            "   ",
            ValueError,
            "timeframe must not be empty",
        ),
        (
            "research_specification",
            object(),
            TypeError,
            "research_specification must be a "
            "ResearchSpecification",
        ),
        (
            "dataset_fingerprint",
            object(),
            TypeError,
            "dataset_fingerprint must be a "
            "MarketDatasetFingerprint",
        ),
        (
            "data_quality_report",
            object(),
            TypeError,
            "data_quality_report must be a "
            "DataQualityReport",
        ),
        (
            "analysis",
            object(),
            TypeError,
            "analysis must be a ComparativeAnalysis",
        ),
        (
            "evaluation_plan",
            object(),
            TypeError,
            "evaluation_plan must be a "
            "ComparativeEvaluationPlan",
        ),
    ),
)
def test_rejects_invalid_arguments(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_result(
            **{field_name: invalid_value}
        )


def test_rejects_indicator_identity_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "indicator_id must match the "
            "research specification"
        ),
    ):
        build_result(
            indicator_id="williams_r"
        )

def build_analysis_with_comparisons(
    *horizons: int,
) -> ComparativeAnalysis:
    analysis = object.__new__(
        ComparativeAnalysis
    )
    comparisons = tuple(
        HorizonComparison(
            horizon=horizon,
            candidate_sample_size=10,
            baseline_sample_size=100,
            mean_return_difference=(
                horizon / 1_000.0
            ),
            median_return_difference=0.0,
            positive_rate_difference=0.0,
        )
        for horizon in horizons
    )
    object.__setattr__(
        analysis,
        "comparisons",
        comparisons,
    )

    return analysis


def build_statistical_evaluation(
    horizon: int,
    **overrides: object,
) -> ComparativeStatisticalEvaluation:
    specification = (
        create_default_research_specification(
            INDICATOR
        )
    )
    arguments: dict[str, object] = {
        "research_fingerprint": (
            specification.fingerprint
        ),
        "dataset_id": "dataset-fingerprint",
        "horizon": horizon,
        "candidate_sample_size": 10,
        "baseline_sample_size": 100,
        "effect_estimate": horizon / 1_000.0,
        "confidence_interval_lower": -0.001,
        "confidence_interval_upper": 0.003,
        "confidence_level": 0.95,
        "method": "moving_block_bootstrap",
        "resample_count": 2_000,
        "block_length": 24,
        "random_seed": 0,
    }
    arguments.update(overrides)

    return ComparativeStatisticalEvaluation(
        **arguments,  # type: ignore[arg-type]
    )


def test_validates_statistical_evaluations(
) -> None:
    analysis = build_analysis_with_comparisons(
        1,
        3,
    )
    first = build_statistical_evaluation(1)
    third = build_statistical_evaluation(3)

    result = build_result(
        analysis=analysis,
        statistical_evaluations=(
            third,
            first,
        ),
    )

    assert result.statistical_evaluations == (
        first,
        third,
    )


@pytest.mark.parametrize(
    (
        "evaluations",
        "error_type",
        "message",
    ),
    [
        (
            [],
            TypeError,
            "statistical_evaluations must be a tuple",
        ),
        (
            (object(),),
            TypeError,
            "each statistical evaluation must be a "
            "ComparativeStatisticalEvaluation",
        ),
    ],
)
def test_rejects_invalid_statistical_collection(
    evaluations: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_result(
            statistical_evaluations=evaluations,
        )


def test_rejects_duplicate_statistical_horizon(
) -> None:
    analysis = build_analysis_with_comparisons(1)
    evaluation = build_statistical_evaluation(1)

    with pytest.raises(
        ValueError,
        match=(
            "statistical evaluations must not "
            "contain duplicate horizons"
        ),
    ):
        build_result(
            analysis=analysis,
            statistical_evaluations=(
                evaluation,
                evaluation,
            ),
        )


def test_rejects_missing_statistical_horizon(
) -> None:
    analysis = build_analysis_with_comparisons(
        1,
        3,
    )

    with pytest.raises(
        ValueError,
        match=(
            "statistical evaluations must cover "
            "all comparison horizons"
        ),
    ):
        build_result(
            analysis=analysis,
            statistical_evaluations=(
                build_statistical_evaluation(1),
            ),
        )


@pytest.mark.parametrize(
    (
        "overrides",
        "message",
    ),
    [
        (
            {
                "research_fingerprint": (
                    "different-research"
                ),
            },
            "statistical evaluation research "
            "fingerprint must match the result",
        ),
        (
            {
                "dataset_id": "different-dataset",
            },
            "statistical evaluation dataset id "
            "must match the result",
        ),
        (
            {
                "candidate_sample_size": 11,
            },
            "statistical evaluation candidate "
            "sample size must match the comparison",
        ),
        (
            {
                "baseline_sample_size": 101,
            },
            "statistical evaluation baseline "
            "sample size must match the comparison",
        ),
        (
            {
                "effect_estimate": 0.5,
            },
            "statistical evaluation effect estimate "
            "must match the comparison",
        ),
    ],
)
def test_rejects_mismatched_statistical_evaluation(
    overrides: dict[str, object],
    message: str,
) -> None:
    analysis = build_analysis_with_comparisons(1)

    with pytest.raises(
        ValueError,
        match=message,
    ):
        build_result(
            analysis=analysis,
            statistical_evaluations=(
                build_statistical_evaluation(
                    1,
                    **overrides,
                ),
            ),
        )

@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "message",
    ),
    [
        (
            "method",
            "stationary_bootstrap",
            "statistical evaluation method "
            "must match the evaluation plan",
        ),
        (
            "confidence_level",
            0.9,
            "statistical evaluation confidence "
            "level must match the evaluation plan",
        ),
        (
            "resample_count",
            100,
            "statistical evaluation resample "
            "count must match the evaluation plan",
        ),
        (
            "block_length",
            12,
            "statistical evaluation block "
            "length must match the evaluation plan",
        ),
        (
            "random_seed",
            7,
            "statistical evaluation random "
            "seed must match the evaluation plan",
        ),
    ],
)
def test_rejects_statistical_plan_mismatch(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    analysis = build_analysis_with_comparisons(1)

    with pytest.raises(
        ValueError,
        match=message,
    ):
        build_result(
            analysis=analysis,
            statistical_evaluations=(
                build_statistical_evaluation(
                    1,
                    **{field_name: invalid_value},
                ),
            ),
        )


def test_preserves_explicit_evaluation_plan(
) -> None:
    plan = ComparativeEvaluationPlan(
        block_length=12,
        random_seed=17,
    )

    result = build_result(
        evaluation_plan=plan,
    )

    assert result.evaluation_plan is plan
    assert result.evaluation_plan_fingerprint == (
        plan.fingerprint
    )
