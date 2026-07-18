from __future__ import annotations

from dataclasses import dataclass

from src.application.market_experiment_executor import (
    MarketExperimentExecutor,
)
from src.research import (
    ExperimentResult,
    ResearchContext,
)
from src.application.prepared_market_backtest_executor import (
    PreparedMarketBacktestExecutor,
)
from src.research.research_graph import (
    ResearchGraph,
)


@dataclass(frozen=True)
class MarketResearchSession:
    """
    Immutable application-level execution session for one market
    research experiment.

    The research graph preserves the identity links between Question,
    Hypothesis, and Experiment.
    """

    context: ResearchContext

    graph: ResearchGraph

    executor: MarketExperimentExecutor

    def __post_init__(self) -> None:
        if self.graph.hypothesis.question_id != self.graph.question.id:
            raise ValueError(
                "hypothesis does not belong to session question"
            )

        if (
            self.graph.experiment.hypothesis_id
            != self.graph.hypothesis.id
        ):
            raise ValueError(
                "experiment does not belong to session hypothesis"
            )

    
    def execute(self) -> ExperimentResult:
        """
        Execute the experiment inside this immutable session.
        """
        return self.executor(
            self.graph.experiment,
        )
