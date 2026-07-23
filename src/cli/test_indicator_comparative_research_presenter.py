import json

import pytest

from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.cli.indicator_comparative_research_presenter import (
    present_indicator_comparative_research_result,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


def build_result(
) -> IndicatorComparativeResearchResult:
    outcome_specification = (
        ForwardReturnSpecification(
            horizons=(1,),
        )
    )
    candidate_result = EventStudyResult(
        specification=outcome_specification,
        observation_ids=("candidate",),
        outcomes=(
            ForwardReturnOutcome(
                observation_id="candidate",
                horizon=1,
                start_bar_index=0,
                start_price=100.0,
                end_price=110.0,
            ),
        ),
    )
    baseline_result = EventStudyResult(
        specification=outcome_specification,
        observation_ids=("baseline",),
        outcomes=(
            ForwardReturnOutcome(
                observation_id="baseline",
                horizon=1,
                start_bar_index=0,
                start_price=100.0,
                end_price=105.0,
            ),
        ),
    )
    analysis = ComparativeAnalysis(
        candidate_result=candidate_result,
        baseline_result=baseline_result,
        candidate_statistics=(
            HorizonStatistics(
                horizon=1,
                sample_size=1,
                mean_return=0.1,
                median_return=0.1,
                positive_rate=1.0,
                minimum_return=0.1,
                maximum_return=0.1,
            ),
        ),
        baseline_statistics=(
            HorizonStatistics(
                horizon=1,
                sample_size=1,
                mean_return=0.05,
                median_return=0.05,
                positive_rate=1.0,
                minimum_return=0.05,
                maximum_return=0.05,
            ),
        ),
        comparisons=(
            HorizonComparison(
                horizon=1,
                candidate_sample_size=1,
                baseline_sample_size=1,
                mean_return_difference=0.05,
                median_return_difference=0.05,
                positive_rate_difference=0.0,
            ),
        ),
    )
    research_specification = (
        ResearchSpecification.create(
            indicator=IndicatorReference(
                indicator_id="test_indicator",
                indicator_version=1,
            ),
            output="value",
            profile=None,
            observation_type=None,
            signal_rule_id="test_rule",
            calculation_parameters={},
            observation_parameters={},
        )
    )

    evaluation_plan = ComparativeEvaluationPlan(
        block_length=1,
        random_seed=7,
    )

    return IndicatorComparativeResearchResult(
        indicator_id="test_indicator",
        symbol="EURUSD",
        timeframe="H1",
        research_specification=(
            research_specification
        ),
        dataset_fingerprint=(
            MarketDatasetFingerprint(
                content_fingerprint="content-id",
                dataset_fingerprint="dataset-id",
                algorithm="sha256",
                content_schema_version="content-v1",
                dataset_schema_version="dataset-v1",
                normalization_schema_version=(
                    "normalization-v1"
                ),
            )
        ),
        data_quality_report=DataQualityReport(
            row_count=2,
            first_timestamp=1,
            last_timestamp=2,
            duplicate_timestamp_count=0,
            missing_timestamp_count=0,
            invalid_ohlc_count=0,
            monotonic_timestamp=True,
        ),
        analysis=analysis,
        evaluation_plan=evaluation_plan,
        statistical_evaluations=(
            ComparativeStatisticalEvaluation(
                research_fingerprint=(
                    research_specification.fingerprint
                ),
                dataset_id="dataset-id",
                horizon=1,
                candidate_sample_size=1,
                baseline_sample_size=1,
                effect_estimate=0.05,
                confidence_interval_lower=0.01,
                confidence_interval_upper=0.09,
                confidence_level=0.95,
                method="moving_block_bootstrap",
                resample_count=2_000,
                block_length=1,
                random_seed=7,
                warnings=(
                    "candidate sample size is below 30",
                ),
            ),
        ),
    )


def test_presents_json_compatible_result(
) -> None:
    expected_plan = ComparativeEvaluationPlan(
        block_length=1,
        random_seed=7,
    )
    payload = (
        present_indicator_comparative_research_result(
            build_result()
        )
    )
    serialized = json.loads(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )

    assert serialized["artifact_type"] == (
        "indicator_comparative_research"
    )
    assert serialized["artifact_version"] == 1
    assert serialized["evaluation_plan"] == {
        "fingerprint": expected_plan.fingerprint,
        "specification": expected_plan.to_dict(),
    }
    assert serialized["indicator"]["id"] == (
        "test_indicator"
    )
    assert serialized["market"] == {
        "symbol": "EURUSD",
        "timeframe": "H1",
    }
    assert serialized["dataset"]["id"] == (
        "dataset-id"
    )
    assert serialized[
        "outcome_specification"
    ] == {
        "horizons": [1],
        "price_field": "close",
    }
    assert serialized[
        "analysis"
    ]["candidate"]["observation_count"] == 1
    assert serialized[
        "analysis"
    ]["candidate"]["outcomes"][0][
        "end_bar_index"
    ] == 1
    assert serialized[
        "analysis"
    ]["candidate"]["outcomes"][0][
        "value"
    ] == pytest.approx(0.1)
    assert serialized[
        "analysis"
    ]["comparisons"][0][
        "mean_return_difference"
    ] == pytest.approx(0.05)

    statistical_evaluation = serialized[
        "analysis"
    ]["statistical_evaluations"][0]

    assert statistical_evaluation["horizon"] == 1
    assert statistical_evaluation[
        "effect_estimate"
    ] == pytest.approx(0.05)
    assert statistical_evaluation[
        "confidence_interval_lower"
    ] == pytest.approx(0.01)
    assert statistical_evaluation[
        "confidence_interval_upper"
    ] == pytest.approx(0.09)
    assert statistical_evaluation[
        "method"
    ] == "moving_block_bootstrap"
    assert statistical_evaluation[
        "excludes_zero"
    ] is True
    assert statistical_evaluation[
        "warnings"
    ] == [
        "candidate sample size is below 30",
    ]


def test_rejects_invalid_result() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "result must be an "
            "IndicatorComparativeResearchResult"
        ),
    ):
        present_indicator_comparative_research_result(
            object()
        )
