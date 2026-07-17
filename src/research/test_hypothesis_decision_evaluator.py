import pytest

from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.hypothesis_decision_evaluator import (
    HypothesisDecisionEvaluator,
)
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


def test_hypothesis_decision_evaluator_supports_hypothesis() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=True,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=False,
    )

    decision = HypothesisDecisionEvaluator().evaluate(
        hypothesis_id="hypothesis-1",
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert decision.experiment_id == "experiment-1"
    assert decision.hypothesis_id == "hypothesis-1"

    assert decision.is_evaluated is True
    assert decision.is_supported is True

    assert decision.result_is_valid is True
    assert decision.statistically_significant is True
    assert decision.robust is True
    assert decision.has_contradiction is False

    assert decision.confidence == pytest.approx(1.0)
    assert decision.failed_requirements == []
    assert decision.warnings == []

    assert (
        decision.basis
        == (
            "Basic validation, inferential statistics, robustness "
            "and contradiction evaluation"
        )
    )


def test_hypothesis_decision_evaluator_rejects_non_significant_result() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=False,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=True,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=False,
    )

    decision = HypothesisDecisionEvaluator().evaluate(
        hypothesis_id="hypothesis-1",
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert decision.is_evaluated is True
    assert decision.is_supported is False

    assert decision.confidence == pytest.approx(0.75)
    assert decision.failed_requirements == [
        "Result is not statistically significant"
    ]


def test_hypothesis_decision_evaluator_rejects_multiple_failures() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=False,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=False,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=False,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=True,
    )

    decision = HypothesisDecisionEvaluator().evaluate(
        hypothesis_id="hypothesis-1",
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert decision.is_evaluated is True
    assert decision.is_supported is False

    assert decision.confidence == pytest.approx(0.0)

    assert decision.failed_requirements == [
        "Experiment result failed basic validation",
        "Result is not statistically significant",
        "Result is not robust",
        "Contradictions were detected",
    ]


def test_hypothesis_decision_evaluator_rejects_different_experiments() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-2",
        is_evaluated=True,
        is_robust=True,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=False,
    )

    decision = HypothesisDecisionEvaluator().evaluate(
        hypothesis_id="hypothesis-1",
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert decision.is_evaluated is False
    assert decision.is_supported is False
    assert decision.confidence == pytest.approx(0.0)

    assert (
        "Evaluation objects belong to different experiments"
        in decision.warnings
    )


def test_hypothesis_decision_evaluator_requires_completed_layers() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=False,
        is_significant=False,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=True,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=False,
        has_contradiction=False,
    )

    decision = HypothesisDecisionEvaluator().evaluate(
        hypothesis_id="hypothesis-1",
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert decision.is_evaluated is False
    assert decision.is_supported is False
    assert decision.confidence == pytest.approx(0.0)

    assert decision.result_is_valid is True
    assert decision.statistically_significant is False
    assert decision.robust is True
    assert decision.has_contradiction is False

    assert (
        "Incomplete evaluation layers: statistical evaluation, "
        "contradiction evaluation"
    ) in decision.warnings