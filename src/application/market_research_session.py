from __future__ import annotations

from dataclasses import dataclass

from src.application.market_experiment_executor import (
    MarketExperimentExecutor,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
    ResearchContext,
)


@dataclass(frozen=True)
class MarketResearchSession:
    """
    Immutable application-level execution session for one market
    research experiment.

    Question, Hypothesis and Experiment must originate from the same
    mapping operation and preserve their research identity links.
    """

    context: ResearchContext

    question: Question

    hypothesis: Hypothesis

    experiment: Experiment

    executor: MarketExperimentExecutor

    def __post_init__(self) -> None:
        if self.hypothesis.question_id != self.question.id:
            raise ValueError(
                "hypothesis does not belong to session question"
            )

        if self.experiment.hypothesis_id != self.hypothesis.id:
            raise ValueError(
                "experiment does not belong to session hypothesis"
            )

    def execute(self) -> ExperimentResult:
        """
        Execute the experiment inside this immutable session.
        """
        return self.executor(
            self.experiment,
        )