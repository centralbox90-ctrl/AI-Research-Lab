from collections.abc import Callable

from src.application.research_cycle_repository import (
    ResearchCycleRepository,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEngine,
)


class RunResearchCycle:
    """
    Application use case for running the complete research MVP pipeline.

    The use case executes the public research API and optionally persists
    the completed research cycle through an application repository.
    """

    def __init__(
        self,
        research_engine: ResearchEngine | None = None,
        repository: ResearchCycleRepository | None = None,
    ) -> None:
        self.research_engine = research_engine or ResearchEngine()
        self.repository = repository

    def execute(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[[Experiment], ExperimentResult],
    ) -> NextExperimentResearchCycleResult:
        cycle = (
            self.research_engine.run_with_next_experiment_selection(
                question=question,
                hypothesis=hypothesis,
                experiment=experiment,
                executor=executor,
            )
        )

        if self.repository is not None:
            self.repository.save(cycle)

        return cycle