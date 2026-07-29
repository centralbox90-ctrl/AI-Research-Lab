from __future__ import annotations

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.experiment_execution_factory import (
    ExperimentExecutionFactory,
)
from src.application.experiment_execution_recorder import (
    ExperimentExecutionRecorder,
)
from src.application.indicator_comparative_execution_specification import (
    IndicatorComparativeExecutionSpecification,
)
from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.application.ports.clock import Clock
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.experiment_execution import (
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
)


class IndicatorComparativeExecutionTracker:
    """
    Records technical execution around one comparative analysis.

    Dataset preparation occurs before this adapter. Statistical
    evaluation occurs after it and cannot change execution status.
    """

    def __init__(
        self,
        *,
        research_service: (
            IndicatorComparativeResearchService
        ),
        execution_factory: ExperimentExecutionFactory,
        execution_recorder: ExperimentExecutionRecorder,
        clock: Clock,
    ) -> None:
        if not callable(
            getattr(research_service, "run", None)
        ):
            raise TypeError(
                "research_service must provide "
                "a callable run method"
            )

        if not callable(
            getattr(
                execution_factory,
                "create_pending_from_fingerprint",
                None,
            )
        ):
            raise TypeError(
                "execution_factory must provide a callable "
                "create_pending_from_fingerprint method"
            )

        if not callable(
            getattr(
                execution_recorder,
                "record",
                None,
            )
        ):
            raise TypeError(
                "execution_recorder must provide "
                "a callable record method"
            )

        if not callable(
            getattr(clock, "now", None)
        ):
            raise TypeError(
                "clock must provide a callable now method"
            )

        self._research_service = research_service
        self._execution_factory = execution_factory
        self._execution_recorder = (
            execution_recorder
        )
        self._clock = clock

    def execute(
        self,
        *,
        dataset: CanonicalMarketDataset,
        specification: (
            IndicatorComparativeExecutionSpecification
        ),
        environment_fingerprint: str,
        correlation_id: str | None = None,
    ) -> ComparativeAnalysis:
        if not isinstance(
            dataset,
            CanonicalMarketDataset,
        ):
            raise TypeError(
                "dataset must be a "
                "CanonicalMarketDataset"
            )

        if not isinstance(
            specification,
            IndicatorComparativeExecutionSpecification,
        ):
            raise TypeError(
                "specification must be an "
                "IndicatorComparativeExecutionSpecification"
            )

        pending = (
            self
            ._execution_factory
            .create_pending_from_fingerprint(
                specification_fingerprint=(
                    specification.fingerprint
                ),
                experiment_id=(
                    "indicator-comparative:"
                    + specification.fingerprint
                ),
                correlation_id=correlation_id,
            )
        )

        running = pending.start(
            environment_fingerprint=(
                environment_fingerprint
            ),
            started_at=self._clock.now(),
        )

        self._execution_recorder.record(
            pending
        )
        self._execution_recorder.record(
            running
        )

        design = IndicatorComparativeResearchDesign(
            research_specification=(
                specification.research_specification
            ),
            outcome_specification=(
                specification.outcome_specification
            ),
            baseline=specification.baseline,
        )
        market = specification.market_specification

        try:
            analysis = self._research_service.run(
                dataset=dataset,
                design=design,
                symbol=market.symbol,
                timeframe=market.timeframe,
            )

            if not isinstance(
                analysis,
                ComparativeAnalysis,
            ):
                raise TypeError(
                    "research service must return "
                    "a ComparativeAnalysis"
                )

            succeeded = running.succeed(
                result_id=(
                    "indicator-comparative-analysis:"
                    + pending.execution_id
                ),
                finished_at=self._clock.now(),
            )
        except Exception as error:
            failed = running.fail(
                failure=ExperimentExecutionFailure(
                    stage=(
                        ExperimentExecutionFailureStage
                        .EXECUTION
                    ),
                    error_type=type(error).__name__,
                    message=(
                        str(error).strip()
                        or type(error).__name__
                    ),
                ),
                finished_at=self._clock.now(),
            )
            self._execution_recorder.record(
                failed
            )
            raise

        self._execution_recorder.record(
            succeeded
        )

        return analysis
