from src.application.market_experiment_executor_registry import (
    MarketExperimentExecutorRegistry,
)
from src.application.market_experiment_mapper import (
    MarketExperimentMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_session_factory import (
    MarketResearchSessionFactory,
)
from src.application.research_cycle_runner import (
    ResearchCycleRunner,
)
from src.research import NextExperimentResearchCycleResult


class RunMarketResearch:
    """
    Runs one market research cycle from a specification.

    Supports two execution modes:

    Legacy mode:
        specification
            ↓
        mapper
            ↓
        executor registry
            ↓
        cycle runner

    Reproducible session mode:
        specification
            ↓
        MarketResearchSessionFactory
            ↓
        ResearchContext + mapped research graph + executor
            ↓
        cycle runner

    Persistence and serialization remain delegated to the supplied
    ResearchCycleRunner.
    """

    def __init__(
        self,
        registry: MarketExperimentExecutorRegistry,
        run_and_store: ResearchCycleRunner,
        mapper: MarketExperimentMapper | None = None,
        session_factory: MarketResearchSessionFactory | None = None,
    ) -> None:
        
        self.registry = registry
        self.run_and_store = run_and_store
        self.mapper = mapper or MarketExperimentMapper()
        self.session_factory = session_factory
        
    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        if self.session_factory is not None:
            return self._execute_reproducible_session(
                specification
            )

        return self._execute_legacy(
            specification
        )

    def _execute_reproducible_session(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        session = self.session_factory.create(
            specification,
        )

        return self.run_and_store.execute(
            specification=specification,
            question=session.question,
            hypothesis=session.hypothesis,
            experiment=session.experiment,
            executor=session.executor,
            research_environment=(
                session.context.environment
            ),
        )

    def _execute_legacy(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        mapped = self.mapper.map(
            specification,
        )

        factory = self.registry.get(
            specification.executor_type,
        )

        executor = factory.create(
            specification,
        )

        return self.run_and_store.execute(
            specification=specification,
            question=mapped.question,
            hypothesis=mapped.hypothesis,
            experiment=mapped.experiment,
            executor=executor,
        )