from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.experiment_execution_factory import (
    ExperimentExecutionFactory,
)
from src.application.indicator_comparative_execution_specification import (
    IndicatorComparativeExecutionSpecification,
)
from src.application.indicator_comparative_execution_tracker import (
    IndicatorComparativeExecutionTracker,
)
from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionStatus,
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


CREATED_AT = datetime(
    2026,
    7,
    29,
    10,
    0,
    tzinfo=UTC,
)
STARTED_AT = CREATED_AT + timedelta(seconds=1)
FINISHED_AT = STARTED_AT + timedelta(seconds=2)
ENVIRONMENT_FINGERPRINT = "b" * 64


class SequenceClock:
    def __init__(
        self,
        *timestamps: datetime,
    ) -> None:
        self._timestamps = list(timestamps)

    def now(self) -> datetime:
        if not self._timestamps:
            raise AssertionError(
                "unexpected clock call"
            )

        return self._timestamps.pop(0)


class StubIdGenerator:
    def generate(self) -> str:
        return "comparative-execution-id"


class RecordingRecorder:
    def __init__(self) -> None:
        self.executions: list[
            ExperimentExecution
        ] = []

    def record(
        self,
        execution: ExperimentExecution,
    ) -> None:
        self.executions.append(execution)


class RecordingResearchService:
    def __init__(
        self,
        result: object,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[
                CanonicalMarketDataset,
                object,
                str,
                str,
            ]
        ] = []

    def run(
        self,
        *,
        dataset: CanonicalMarketDataset,
        design: object,
        symbol: str,
        timeframe: str,
    ) -> object:
        self.calls.append(
            (
                dataset,
                design,
                symbol,
                timeframe,
            )
        )

        return self.result


class FailingResearchService:
    def run(
        self,
        **kwargs: object,
    ) -> ComparativeAnalysis:
        raise RuntimeError(
            "comparative analysis failed"
        )


def build_market_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does RSI predict returns?",
        question_description=(
            "Test RSI on generated data."
        ),
        hypothesis_title="RSI predicts returns",
        hypothesis_description=(
            "Returns differ after RSI observations."
        ),
        expected_result=(
            "A measurable return difference."
        ),
        experiment_title="RSI comparison",
        experiment_description=(
            "Compare RSI observations with a baseline."
        ),
        data_source="generated",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        end_at=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        entry_rule="unused_entry",
        exit_rule="unused_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def build_research_specification(
) -> ResearchSpecification:
    return ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="rsi",
            indicator_version=1,
        ),
        output="value",
        profile=None,
        observation_type="direction",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={},
    )


def build_execution_specification(
) -> IndicatorComparativeExecutionSpecification:
    return (
        IndicatorComparativeExecutionSpecification(
            market_specification=(
                build_market_specification()
            ),
            research_specification=(
                build_research_specification()
            ),
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1,),
                )
            ),
        )
    )


def build_dataset() -> CanonicalMarketDataset:
    return CanonicalMarketDataset(
        data=pd.DataFrame(),
        fingerprint=MarketDatasetFingerprint(
            content_fingerprint=(
                "content-fingerprint"
            ),
            dataset_fingerprint="dataset-id",
            algorithm="sha256",
            content_schema_version=(
                "market-bars-content-v1"
            ),
            dataset_schema_version=(
                "market-dataset-fingerprint-v1"
            ),
            normalization_schema_version=(
                "market-dataset-v1"
            ),
        ),
        quality_report=DataQualityReport(
            row_count=1,
            first_timestamp=1,
            last_timestamp=1,
            duplicate_timestamp_count=0,
            missing_timestamp_count=0,
            invalid_ohlc_count=0,
            monotonic_timestamp=True,
        ),
    )


def build_analysis() -> ComparativeAnalysis:
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
                end_price=101.0,
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
                end_price=100.0,
            ),
        ),
    )
    candidate_statistics = HorizonStatistics(
        horizon=1,
        sample_size=1,
        mean_return=0.01,
        median_return=0.01,
        positive_rate=1.0,
        minimum_return=0.01,
        maximum_return=0.01,
    )
    baseline_statistics = HorizonStatistics(
        horizon=1,
        sample_size=1,
        mean_return=0.0,
        median_return=0.0,
        positive_rate=0.0,
        minimum_return=0.0,
        maximum_return=0.0,
    )

    return ComparativeAnalysis(
        candidate_result=candidate_result,
        baseline_result=baseline_result,
        candidate_statistics=(
            candidate_statistics,
        ),
        baseline_statistics=(
            baseline_statistics,
        ),
        comparisons=(
            HorizonComparison(
                horizon=1,
                candidate_sample_size=1,
                baseline_sample_size=1,
                mean_return_difference=0.01,
                median_return_difference=0.01,
                positive_rate_difference=1.0,
            ),
        ),
    )


def build_tracker(
    research_service: object,
) -> tuple[
    IndicatorComparativeExecutionTracker,
    RecordingRecorder,
]:
    clock = SequenceClock(
        CREATED_AT,
        STARTED_AT,
        FINISHED_AT,
    )
    recorder = RecordingRecorder()
    execution_factory = ExperimentExecutionFactory(
        clock=clock,
        id_generator=StubIdGenerator(),
    )

    return (
        IndicatorComparativeExecutionTracker(
            research_service=research_service,
            execution_factory=execution_factory,
            execution_recorder=recorder,
            clock=clock,
        ),
        recorder,
    )


def test_records_comparative_execution_lifecycle(
) -> None:
    analysis = build_analysis()
    service = RecordingResearchService(
        analysis
    )
    tracker, recorder = build_tracker(
        service
    )
    dataset = build_dataset()
    specification = (
        build_execution_specification()
    )

    result = tracker.execute(
        dataset=dataset,
        specification=specification,
        environment_fingerprint=(
            ENVIRONMENT_FINGERPRINT
        ),
        correlation_id="research-lifecycle-42",
    )

    assert result is analysis
    assert [
        execution.status
        for execution in recorder.executions
    ] == [
        ExperimentExecutionStatus.PENDING,
        ExperimentExecutionStatus.RUNNING,
        ExperimentExecutionStatus.SUCCEEDED,
    ]

    pending, running, succeeded = (
        recorder.executions
    )

    assert pending.specification_fingerprint == (
        specification.fingerprint
    )
    assert pending.experiment_id == (
        "indicator-comparative:"
        + specification.fingerprint
    )
    assert pending.correlation_id == (
        "research-lifecycle-42"
    )
    assert running.environment_fingerprint == (
        ENVIRONMENT_FINGERPRINT
    )
    assert succeeded.result_id == (
        "indicator-comparative-analysis:"
        "comparative-execution-id"
    )
    assert succeeded.created_at == CREATED_AT
    assert succeeded.started_at == STARTED_AT
    assert succeeded.finished_at == FINISHED_AT
    assert len(service.calls) == 1

    _, design, symbol, timeframe = (
        service.calls[0]
    )

    assert symbol == "EURUSD"
    assert timeframe == "H1"
    assert design.research_specification == (
        specification.research_specification
    )
    assert design.outcome_specification == (
        specification.outcome_specification
    )


def test_records_failed_comparative_execution(
) -> None:
    tracker, recorder = build_tracker(
        FailingResearchService()
    )

    with pytest.raises(
        RuntimeError,
        match="comparative analysis failed",
    ):
        tracker.execute(
            dataset=build_dataset(),
            specification=(
                build_execution_specification()
            ),
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
        )

    assert [
        execution.status
        for execution in recorder.executions
    ] == [
        ExperimentExecutionStatus.PENDING,
        ExperimentExecutionStatus.RUNNING,
        ExperimentExecutionStatus.FAILED,
    ]

    failure = recorder.executions[-1].failure

    assert failure is not None
    assert failure.error_type == "RuntimeError"
    assert failure.message == (
        "comparative analysis failed"
    )


def test_invalid_analysis_is_execution_failure(
) -> None:
    tracker, recorder = build_tracker(
        RecordingResearchService(object())
    )

    with pytest.raises(
        TypeError,
        match=(
            "research service must return "
            "a ComparativeAnalysis"
        ),
    ):
        tracker.execute(
            dataset=build_dataset(),
            specification=(
                build_execution_specification()
            ),
            environment_fingerprint=(
                ENVIRONMENT_FINGERPRINT
            ),
        )

    failed = recorder.executions[-1]

    assert failed.status is (
        ExperimentExecutionStatus.FAILED
    )
    assert failed.failure is not None
    assert failed.failure.error_type == "TypeError"


def test_invalid_environment_is_not_recorded(
) -> None:
    clock = SequenceClock(
        CREATED_AT,
        STARTED_AT,
    )
    recorder = RecordingRecorder()
    tracker = IndicatorComparativeExecutionTracker(
        research_service=(
            RecordingResearchService(
                build_analysis()
            )
        ),
        execution_factory=(
            ExperimentExecutionFactory(
                clock=clock,
                id_generator=StubIdGenerator(),
            )
        ),
        execution_recorder=recorder,
        clock=clock,
    )

    with pytest.raises(
        ValueError,
        match=(
            "environment_fingerprint must be "
            "a lowercase SHA-256 hexadecimal string"
        ),
    ):
        tracker.execute(
            dataset=build_dataset(),
            specification=(
                build_execution_specification()
            ),
            environment_fingerprint="invalid",
        )

    assert recorder.executions == []
