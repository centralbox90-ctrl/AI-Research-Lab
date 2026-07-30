from __future__ import annotations

from src.application.experiment_execution_factory import (
    ExperimentExecutionFactory,
)
from src.application.experiment_execution_recorder import (
    ExperimentExecutionRecorder,
)
from src.application.experiment_execution_tracking_executor import (
    ExperimentExecutionTrackingExecutor,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
)
from src.application.market_experiment_mapper import (
    MarketExperimentMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_context_factory import (
    MarketResearchContextFactory,
)
from src.application.market_research_session import (
    MarketResearchSession,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.application.ports.clock import Clock
from src.application.prepared_market_backtest_executor import (
    PreparedMarketBacktestExecutor,
)
from src.application.system_clock import SystemClock
from src.research.experiment_execution import (
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
)
from src.research.research_graph import (
    ResearchGraph,
)


class MarketResearchSessionFactory:
    """
    Creates one immutable market research session.
    """

    def __init__(
        self,
        *,
        data_provider: CanonicalMarketDatasetProvider,
        signal_provider: MarketSignalProvider,
        context_factory: MarketResearchContextFactory,
        execution_recorder: ExperimentExecutionRecorder,
        mapper: MarketExperimentMapper | None = None,
        clock: Clock | None = None,
        execution_factory: (
            ExperimentExecutionFactory | None
        ) = None,
    ) -> None:
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

        self._data_provider = data_provider
        self._signal_provider = signal_provider
        self._context_factory = context_factory
        self._execution_recorder = execution_recorder
        self._clock = clock or SystemClock()
        self._execution_factory = (
            execution_factory
            or ExperimentExecutionFactory(
                clock=self._clock,
            )
        )
        self._mapper = (
            mapper
            or MarketExperimentMapper()
        )

    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> MarketResearchSession:
        mapped = self._mapper.map(
            specification
        )

        graph = ResearchGraph(
            question=mapped.question,
            hypothesis=mapped.hypothesis,
            experiment=mapped.experiment,
        )

        execution = (
            self._execution_factory.create_pending(
                specification=specification,
                experiment_id=graph.experiment.id,
            )
        )

        try:
            dataset = self._data_provider.load(
                specification
            )

            context = self._context_factory.create(
                specification=specification,
                dataset=dataset,
            )

            prepared_executor = (
                PreparedMarketBacktestExecutor(
                    specification=specification,
                    market_data=context.market_data,
                    signal_provider=(
                        self._signal_provider
                    ),
                )
            )

            executor = (
                ExperimentExecutionTrackingExecutor(
                    executor=prepared_executor,
                    execution=execution,
                    environment_fingerprint=(
                        context.environment.fingerprint()
                    ),
                    recorder=(
                        self._execution_recorder
                    ),
                    clock=self._clock,
                )
            )
        except Exception as error:
            failure = ExperimentExecutionFailure(
                stage=(
                    ExperimentExecutionFailureStage
                    .PREPARATION
                ),
                error_type=type(error).__name__,
                message=(
                    str(error).strip()
                    or type(error).__name__
                ),
            )
            failed = execution.fail(
                failure=failure,
                finished_at=self._clock.now(),
            )

            self._execution_recorder.record(
                execution
            )
            self._execution_recorder.record(
                failed
            )

            raise

        return MarketResearchSession(
            context=context,
            graph=graph,
            executor=executor,
        )