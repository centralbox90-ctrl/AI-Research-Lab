from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.hypothesis_decision import HypothesisDecision
from src.research.next_experiment_selector import NextExperimentSelector
from src.research.robustness_evaluation import RobustnessEvaluation
from src.research.statistical_evaluation import StatisticalEvaluation


def test_next_experiment_selector_collects_observations() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=False,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=False,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=False,
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=False,
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "collect_observations"
    assert selection.priority == "critical"
    assert selection.target_requirement == "statistical_evaluation"


def test_next_experiment_selector_increases_sample_size() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_significant=False,
            sample_size=3,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_robust=False,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            score=0.40,
            level="weak",
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=True,
            is_supported=False,
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "increase_sample_size"
    assert selection.priority == "high"
    assert selection.target_requirement == "sample_size"


def test_next_experiment_selector_improves_significance() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_significant=False,
            sample_size=10,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_robust=True,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            score=0.60,
            level="moderate",
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=True,
            is_supported=False,
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "improve_statistical_significance"
    assert selection.priority == "high"
    assert selection.target_requirement == "statistical_significance"


def test_next_experiment_selector_tests_robustness() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_significant=True,
            sample_size=10,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_robust=False,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            score=0.70,
            level="moderate",
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=True,
            is_supported=False,
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "test_robustness"
    assert selection.priority == "high"
    assert selection.target_requirement == "robustness"


def test_next_experiment_selector_resolves_contradiction() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_significant=True,
            sample_size=10,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_robust=True,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            score=0.60,
            level="moderate",
            has_contradiction=True,
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=True,
            is_supported=False,
            failed_requirements=["contradiction_absence"],
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "resolve_contradiction"
    assert selection.priority == "critical"
    assert selection.target_requirement == "contradiction_absence"

    assert selection.failed_requirements == [
        "contradiction_absence"
    ]


def test_next_experiment_selector_replicates_supported_hypothesis() -> None:
    selection = NextExperimentSelector().select(
        hypothesis_id="hypothesis-1",
        statistical_evaluation=StatisticalEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_significant=True,
            sample_size=10,
        ),
        robustness_evaluation=RobustnessEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            is_robust=True,
        ),
        evidence_strength_evaluation=EvidenceStrengthEvaluation(
            experiment_id="experiment-1",
            is_evaluated=True,
            score=0.95,
            level="very_strong",
            has_contradiction=False,
        ),
        hypothesis_decision=HypothesisDecision(
            hypothesis_id="hypothesis-1",
            is_evaluated=True,
            is_supported=True,
            confidence=1.0,
        ),
    )

    assert selection.is_selected is True
    assert selection.action == "replicate_experiment"
    assert selection.priority == "low"
    assert selection.target_requirement == "independent_replication"

    assert selection.evidence_strength_score == 0.95
    assert selection.evidence_strength_level == "very_strong"
    assert selection.failed_requirements == []
    assert selection.warnings == []