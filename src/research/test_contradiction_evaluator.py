from src.research.contradiction_evaluator import (
    ContradictionEvaluator,
)
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


def test_contradiction_evaluator_detects_no_conflict() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        mean=2.0,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=True,
        first_half_mean=1.5,
        second_half_mean=2.5,
        direction_consistent=True,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is True
    assert evaluation.has_contradiction is False

    assert evaluation.observed_direction == "positive"
    assert evaluation.statistically_significant is True
    assert evaluation.robust is True

    assert evaluation.significance_robustness_conflict is False
    assert evaluation.direction_robustness_conflict is False
    assert evaluation.contradiction_count == 0

    assert evaluation.warnings == []


def test_contradiction_evaluator_detects_significance_conflict() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        mean=2.0,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=False,
        first_half_mean=1.0,
        second_half_mean=-0.5,
        direction_consistent=False,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.is_evaluated is True
    assert evaluation.has_contradiction is True

    assert evaluation.observed_direction == "positive"
    assert evaluation.statistically_significant is True
    assert evaluation.robust is False

    assert evaluation.significance_robustness_conflict is True
    assert evaluation.direction_robustness_conflict is False
    assert evaluation.contradiction_count == 1


def test_contradiction_evaluator_detects_direction_conflict() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=False,
        mean=1.0,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=True,
        first_half_mean=-2.0,
        second_half_mean=-1.0,
        direction_consistent=True,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.is_evaluated is True
    assert evaluation.has_contradiction is True

    assert evaluation.observed_direction == "positive"
    assert evaluation.statistically_significant is False
    assert evaluation.robust is True

    assert evaluation.significance_robustness_conflict is False
    assert evaluation.direction_robustness_conflict is True
    assert evaluation.contradiction_count == 1


def test_contradiction_evaluator_detects_multiple_conflicts() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        mean=1.0,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=False,
        first_half_mean=-2.0,
        second_half_mean=-1.0,
        direction_consistent=True,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.is_evaluated is True
    assert evaluation.has_contradiction is True

    assert evaluation.significance_robustness_conflict is True
    assert evaluation.direction_robustness_conflict is True
    assert evaluation.contradiction_count == 2


def test_contradiction_evaluator_rejects_different_experiments() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        mean=2.0,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-2",
        is_evaluated=True,
        is_robust=True,
        first_half_mean=1.0,
        second_half_mean=2.0,
        direction_consistent=True,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.is_evaluated is False
    assert evaluation.has_contradiction is False
    assert evaluation.contradiction_count == 0

    assert (
        "Statistical and robustness evaluations belong "
        "to different experiments"
    ) in evaluation.warnings


def test_contradiction_evaluator_requires_completed_evaluations() -> None:
    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=False,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=False,
    )

    evaluation = ContradictionEvaluator().evaluate(
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
    )

    assert evaluation.is_evaluated is False
    assert evaluation.has_contradiction is False

    assert "Statistical evaluation is incomplete" in evaluation.warnings
    assert "Robustness evaluation is incomplete" in evaluation.warnings