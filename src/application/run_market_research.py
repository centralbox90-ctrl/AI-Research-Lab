from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_session_factory import (
    MarketResearchSessionFactory,
)
from src.application.research_cycle_runner import (
    ResearchCycleRunner,
)
from src.research import (
    NextExperimentResearchCycleResult,
)


class RunMarketResearch:
    """
    Runs one reproducible market research cycle from a specification.

    The session factory builds the research context, mapped research
    graph, prepared market data, and experiment executor.

    Persistence and serialization remain delegated to the supplied
    ResearchCycleRunner.
    """

    def __init__(
        self,
        *,
        run_and_store: ResearchCycleRunner,
        session_factory: MarketResearchSessionFactory,
    ) -> None:
        self._run_and_store = run_and_store
        self._session_factory = session_factory

    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> NextExperimentResearchCycleResult:
        session = self._session_factory.create(
            specification,
        )

        return self._run_and_store.execute(
            specification=specification,
            question=session.graph.question,
            hypothesis=session.graph.hypothesis,
            experiment=session.graph.experiment,
            executor=session.executor,
            research_environment=(
                session.context.environment
            ),
        )
