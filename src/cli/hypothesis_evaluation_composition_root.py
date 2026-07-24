from __future__ import annotations

from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)
from src.research.hypothesis_evaluator import (
    HypothesisEvaluator,
)


def build_default_hypothesis_evaluation_application(
    *,
    plan: HypothesisEvaluationPlan = (
        HypothesisEvaluationPlan()
    ),
) -> HypothesisEvaluationApplication:
    """Build the formal hypothesis evaluation application."""

    return HypothesisEvaluationApplication(
        hypothesis_evaluator=HypothesisEvaluator(
            plan=plan,
        ),
    )