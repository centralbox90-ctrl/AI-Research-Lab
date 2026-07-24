from __future__ import annotations

from src.research.finding import Finding
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
)
from src.research.hypothesis_evaluator import (
    HypothesisEvaluator,
)


class HypothesisEvaluationApplication:
    """
    Application boundary for formal hypothesis evaluation.
    """

    def __init__(
        self,
        *,
        hypothesis_evaluator: HypothesisEvaluator,
    ) -> None:
        if not isinstance(
            hypothesis_evaluator,
            HypothesisEvaluator,
        ):
            raise TypeError(
                "hypothesis_evaluator must be a "
                "HypothesisEvaluator"
            )

        self._hypothesis_evaluator = (
            hypothesis_evaluator
        )

    def run(
        self,
        *,
        findings: tuple[Finding, ...],
    ) -> HypothesisEvaluation:
        return self._hypothesis_evaluator.evaluate(
            findings=findings,
        )