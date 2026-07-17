import pytest

from src.research.contradiction_evaluation import (
    ContradictionEvaluation,
)
from src.research.evidence_strength_evaluator import (
    EvidenceStrengthEvaluator,
)
from src.research.experiment_evaluation import ExperimentEvaluation
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


def test_evidence_strength_evaluator_calculates_very_strong_score() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        p_value=0.001,
        effect_size=1.0,
        significance_level=0.05,
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

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is True

    assert evaluation.score == pytest.approx(0.998)
    assert evaluation.level == "very_strong"

    assert evaluation.result_is_valid is True
    assert evaluation.statistically_significant is True
    assert evaluation.p_value == pytest.approx(0.001)
    assert evaluation.effect_size == pytest.approx(1.0)
    assert evaluation.robust is True
    assert evaluation.has_contradiction is False

    assert evaluation.component_scores == pytest.approx(
        {
            "validation": 1.0,
            "statistical_significance": 1.0,
            "p_value_strength": 0.98,
            "effect_size_strength": 1.0,
            "robustness": 1.0,
            "contradiction_absence": 1.0,
        }
    )

    assert evaluation.warnings == []


def test_evidence_strength_evaluator_calculates_weak_score() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=False,
        p_value=0.50,
        effect_size=0.20,
        significance_level=0.05,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=False,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=False,
    )

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.is_evaluated is True

    assert evaluation.score == pytest.approx(0.425)
    assert evaluation.level == "weak"

    assert evaluation.component_scores == pytest.approx(
        {
            "validation": 1.0,
            "statistical_significance": 0.0,
            "p_value_strength": 0.0,
            "effect_size_strength": 0.25,
            "robustness": 0.0,
            "contradiction_absence": 1.0,
        }
    )


def test_evidence_strength_evaluator_penalizes_contradictions() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        p_value=0.001,
        effect_size=1.0,
        significance_level=0.05,
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

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.is_evaluated is True

    assert evaluation.score == pytest.approx(0.498)
    assert evaluation.level == "weak"

    assert evaluation.component_scores["robustness"] == pytest.approx(
        0.0
    )
    assert evaluation.component_scores[
        "contradiction_absence"
    ] == pytest.approx(0.0)


def test_evidence_strength_evaluator_uses_absolute_effect_size() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=False,
        p_value=0.50,
        effect_size=-0.40,
        significance_level=0.05,
    )

    robustness_evaluation = RobustnessEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_robust=False,
    )

    contradiction_evaluation = ContradictionEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        has_contradiction=False,
    )

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.is_evaluated is True

    assert evaluation.component_scores[
        "effect_size_strength"
    ] == pytest.approx(0.5)

    assert evaluation.score == pytest.approx(0.45)
    assert evaluation.level == "weak"


def test_evidence_strength_evaluator_rejects_different_experiments() -> None:
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

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.is_evaluated is False
    assert evaluation.score == pytest.approx(0.0)
    assert evaluation.level == "unknown"

    assert (
        "Evaluation objects belong to different experiments"
        in evaluation.warnings
    )


def test_evidence_strength_evaluator_requires_completed_layers() -> None:
    experiment_evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
    )

    statistical_evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=False,
        is_significant=False,
        p_value=None,
        effect_size=None,
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

    evaluation = EvidenceStrengthEvaluator().evaluate(
        experiment_evaluation=experiment_evaluation,
        statistical_evaluation=statistical_evaluation,
        robustness_evaluation=robustness_evaluation,
        contradiction_evaluation=contradiction_evaluation,
    )

    assert evaluation.is_evaluated is False
    assert evaluation.score == pytest.approx(0.0)
    assert evaluation.level == "unknown"

    assert evaluation.result_is_valid is True
    assert evaluation.statistically_significant is False
    assert evaluation.p_value is None
    assert evaluation.effect_size is None
    assert evaluation.robust is True
    assert evaluation.has_contradiction is False

    assert (
        "Incomplete evaluation layers: statistical evaluation, "
        "contradiction evaluation"
    ) in evaluation.warnings