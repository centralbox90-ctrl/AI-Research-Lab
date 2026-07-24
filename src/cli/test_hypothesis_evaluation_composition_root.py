from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.cli.hypothesis_evaluation_composition_root import (
    build_default_hypothesis_evaluation_application,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)
from src.research.hypothesis_evaluator import (
    HypothesisEvaluator,
)


def test_builds_application_with_declared_plan(
) -> None:
    plan = HypothesisEvaluationPlan(
        version="hypothesis-evaluation-custom",
        supported_confidence_threshold=0.8,
        partially_supported_confidence_threshold=(
            0.6
        ),
        rejected_confidence_threshold=0.85,
        minimum_decisive_findings=3,
    )

    application = (
        build_default_hypothesis_evaluation_application(
            plan=plan,
        )
    )

    assert isinstance(
        application,
        HypothesisEvaluationApplication,
    )
    assert isinstance(
        application._hypothesis_evaluator,
        HypothesisEvaluator,
    )
    assert (
        application
        ._hypothesis_evaluator
        ._plan
        is plan
    )


def test_builds_application_with_default_plan(
) -> None:
    application = (
        build_default_hypothesis_evaluation_application()
    )
    plan = (
        application
        ._hypothesis_evaluator
        ._plan
    )

    assert isinstance(
        plan,
        HypothesisEvaluationPlan,
    )
    assert plan.version == (
        "hypothesis-evaluation-v1"
    )
    assert plan.minimum_decisive_findings == 2