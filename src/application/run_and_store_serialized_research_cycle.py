from collections.abc import Callable

from src.application.research_cycle_serializer import (
    ResearchCycleSerializer,
)
from src.application.serialized_research_cycle_store import (
    SerializedResearchCycleStore,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEngine,
)


class RunAndStoreSerializedResearchCycle:
    """
    Runs the complete research cycle and stores serialized output.

    This use case keeps research execution, serialization, and serialized
    persistence coordinated at the application layer.
    """

    def __init__(
        self,
        store: SerializedResearchCycleStore,
        research_engine: ResearchEngine | None = None,
        serializer: ResearchCycleSerializer | None = None,
    ) -> None:
        self.store = store
        self.research_engine = research_engine or ResearchEngine()
        self.serializer = serializer or ResearchCycleSerializer()

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

        serialized_cycle = self.serializer.serialize(cycle)

        self.store.save(
            result_id=cycle.result.id,
            serialized_cycle=serialized_cycle,
        )

        return cycle