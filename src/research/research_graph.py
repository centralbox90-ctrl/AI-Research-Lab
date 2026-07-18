from dataclasses import dataclass

from src.research.experiment import Experiment
from src.research.hypothesis import Hypothesis
from src.research.question import Question


@dataclass(frozen=True)
class ResearchGraph:
    """
    Canonical research graph for one research cycle.

    Represents the causal chain:

        Question
            ↓
        Hypothesis
            ↓
        Experiment
    """

    question: Question

    hypothesis: Hypothesis

    experiment: Experiment
