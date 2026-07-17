from collections.abc import Callable
from typing import Protocol

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
)


class ResearchCycleRunner(Protocol):
    """
    Application boundary for running and storing a market research cycle.

    Implementations may choose different serialization and persistence
    formats, but must accept the original market specification together
    with the mapped research-core objects.
    """

    def execute(
        self,
        specification: MarketExperimentSpecification,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: Callable[
            [Experiment],
            ExperimentResult,
        ],
    ) -> NextExperimentResearchCycleResult:
        """
        Run and store one market research cycle.
        """