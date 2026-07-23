from dataclasses import replace

import pytest

from src.application.indicator_comparative_evidence_service import (
    IndicatorComparativeEvidenceService,
)
from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.indicators.descriptor import IndicatorDescriptor
from src.indicators.implementations.rsi import (
    INDICATOR as RSI_INDICATOR,
)
from src.indicators.implementations.williams_r import (
    INDICATOR as WILLIAMS_R_INDICATOR,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_evidence_evaluator import (
    ComparativeEvidenceEvaluator,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.evidence import EvidenceDirection
from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.specification import (
    ResearchSpecification,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


def build_dataset_fingerprint(
    dataset_id: str,
) -> MarketDatasetFingerprint:
    return MarketDatasetFingerprint(
        content_fingerprint=(
            f"content:{dataset_id}"
        ),
        dataset_fingerprint=dataset_id,
        algorithm="sha256",
        content_schema_version="content-v1",
        dataset_schema_version="dataset-v1",
        normalization_schema_version=(
            "normalization-v1"
        ),
    )


def build_quality_report() -> DataQualityReport:
    return DataQualityReport(
        row_count=500,
        first_timestamp=1_700_000_000_000_000_000,
        last_timestamp=1_701_796_400_000_000_000,
        duplicate_timestamp_count=0,
        missing_timestamp_count=0,
        invalid_ohlc_count=0,
        monotonic_timestamp=True,
    )


def build_analysis(
    horizons: tuple[int, ...],
) -> ComparativeAnalysis:
    analysis = object.__new__(
        ComparativeAnalysis
    )
    comparisons = tuple(
        HorizonComparison(
            horizon=horizon,
            candidate_sample_size=100,
            baseline_sample_size=500,
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


def build_evaluation(
    *,
    specification: ResearchSpecification,
    dataset_id: str,
    horizon: int,
    plan: ComparativeEvaluationPlan,
) -> ComparativeStatisticalEvaluation:
    effect = horizon / 1_000.0

    return ComparativeStatisticalEvaluation(
        research_fingerprint=(
            specification.fingerprint
        ),
        dataset_id=dataset_id,
        horizon=horizon,
        candidate_sample_size=100,
        baseline_sample_size=500,
        effect_estimate=effect,
        confidence_interval_lower=(
            effect / 2.0
        ),
        confidence_interval_upper=(
            effect * 1.5
        ),
        confidence_level=(
            plan.confidence_level
        ),
        method=plan.method,
        resample_count=plan.resample_count,
        block_length=plan.block_length,
        random_seed=plan.random_seed,
    )


def build_result(
    dataset_id: str,
    *,
    descriptor: IndicatorDescriptor = (
        RSI_INDICATOR
    ),
    symbol: str = "EURUSD",
    timeframe: str = "H1",
    horizons: tuple[int, ...] = (3, 5),
    plan: ComparativeEvaluationPlan | None = None,
    research_variant: bool = False,
) -> IndicatorComparativeResearchResult:
    selected_plan = (
        ComparativeEvaluationPlan()
        if plan is None
        else plan
    )
    specification = (
        create_default_research_specification(
            descriptor
        )
    )

    if research_variant:
        specification = replace(
            specification,
            signal_rule_id=(
                "different-indicator-direction"
            ),
        )

    return IndicatorComparativeResearchResult(
        indicator_id=descriptor.id,
        symbol=symbol,
        timeframe=timeframe,
        research_specification=specification,
        dataset_fingerprint=(
            build_dataset_fingerprint(
                dataset_id
            )
        ),
        data_quality_report=(
            build_quality_report()
        ),
        analysis=build_analysis(horizons),
        evaluation_plan=selected_plan,
        statistical_evaluations=tuple(
            build_evaluation(
                specification=specification,
                dataset_id=dataset_id,
                horizon=horizon,
                plan=selected_plan,
            )
            for horizon in horizons
        ),
    )


def build_service(
) -> IndicatorComparativeEvidenceService:
    return IndicatorComparativeEvidenceService(
        evidence_evaluator=(
            ComparativeEvidenceEvaluator()
        ),
    )


def test_builds_evidence_from_compatible_results(
) -> None:
    evidence = build_service().evaluate(
        hypothesis_id="  hypothesis-rsi  ",
        results=(
            build_result("dataset-b"),
            build_result("dataset-a"),
        ),
        horizon=3,
    )

    assert evidence.hypothesis_id == (
        "hypothesis-rsi"
    )
    assert evidence.direction is (
        EvidenceDirection.SUPPORTING
    )
    assert evidence.observation_refs == (
        "dataset-a:horizon:3",
        "dataset-b:horizon:3",
    )
    assert evidence.applicability == (
        "indicator:rsi",
        "symbol:EURUSD",
        "timeframe:H1",
        "horizon:3",
    )

    provenance = dict(evidence.provenance)

    assert provenance["horizon"] == "3"
    assert provenance[
        "replication_count"
    ] == "2"
    assert provenance["dataset_ids"] == (
        '["dataset-a","dataset-b"]'
    )


def test_is_order_independent() -> None:
    first = build_result("dataset-a")
    second = build_result("dataset-b")

    original = build_service().evaluate(
        hypothesis_id="hypothesis-rsi",
        results=(
            first,
            second,
        ),
        horizon=3,
    )
    reversed_result = build_service().evaluate(
        hypothesis_id="hypothesis-rsi",
        results=(
            second,
            first,
        ),
        horizon=3,
    )

    assert original == reversed_result
    assert original.fingerprint == (
        reversed_result.fingerprint
    )


def test_rejects_invalid_evaluator() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "evidence_evaluator must be a "
            "ComparativeEvidenceEvaluator"
        ),
    ):
        IndicatorComparativeEvidenceService(
            evidence_evaluator=object(),
        )


@pytest.mark.parametrize(
    (
        "results",
        "error_type",
        "message",
    ),
    (
        (
            [],
            TypeError,
            "results must be a tuple",
        ),
        (
            (),
            ValueError,
            "results must not be empty",
        ),
        (
            (object(),),
            TypeError,
            "each result must be an "
            "IndicatorComparativeResearchResult",
        ),
    ),
)
def test_rejects_invalid_result_collection(
    results: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_service().evaluate(
            hypothesis_id="hypothesis-rsi",
            results=results,  # type: ignore[arg-type]
            horizon=3,
        )


def test_rejects_duplicate_dataset() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "results must use distinct datasets"
        ),
    ):
        build_service().evaluate(
            hypothesis_id="hypothesis-rsi",
            results=(
                build_result("dataset-a"),
                build_result("dataset-a"),
            ),
            horizon=3,
        )


@pytest.mark.parametrize(
    (
        "second_overrides",
        "message",
    ),
    (
        (
            {
                "descriptor": (
                    WILLIAMS_R_INDICATOR
                ),
            },
            "results must use the same indicator",
        ),
        (
            {
                "symbol": "GBPUSD",
            },
            "results must use the same symbol",
        ),
        (
            {
                "timeframe": "M15",
            },
            "results must use the same timeframe",
        ),
        (
            {
                "research_variant": True,
            },
            "results must use the same "
            "research fingerprint",
        ),
        (
            {
                "plan": (
                    ComparativeEvaluationPlan(
                        random_seed=17,
                    )
                ),
            },
            "results must use the same "
            "evaluation plan",
        ),
    ),
)
def test_rejects_incompatible_results(
    second_overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        build_service().evaluate(
            hypothesis_id="hypothesis-rsi",
            results=(
                build_result("dataset-a"),
                build_result(
                    "dataset-b",
                    **second_overrides,
                ),
            ),
            horizon=3,
        )


def test_rejects_missing_horizon() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "result dataset 'dataset-b' "
            "does not contain horizon 3"
        ),
    ):
        build_service().evaluate(
            hypothesis_id="hypothesis-rsi",
            results=(
                build_result(
                    "dataset-a",
                    horizons=(3,),
                ),
                build_result(
                    "dataset-b",
                    horizons=(5,),
                ),
            ),
            horizon=3,
        )


@pytest.mark.parametrize(
    (
        "horizon",
        "error_type",
        "message",
    ),
    (
        (
            True,
            TypeError,
            "horizon must be an integer",
        ),
        (
            0,
            ValueError,
            "horizon must be positive",
        ),
        (
            -1,
            ValueError,
            "horizon must be positive",
        ),
    ),
)
def test_rejects_invalid_horizon(
    horizon: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_service().evaluate(
            hypothesis_id="hypothesis-rsi",
            results=(
                build_result("dataset-a"),
            ),
            horizon=horizon,  # type: ignore[arg-type]
        )
