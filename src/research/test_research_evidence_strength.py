import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_cycle_with_evidence_strength() -> None:
    question = Question(
        title="Evidence strength research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Evidence strength experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
                "total_trades": 5,
            },
            observations={
                "profit_percent": [1.8, 2.0, 2.1, 1.9, 2.2],
            },
            conclusion="Experiment completed successfully",
        )

    (
        result,
        evaluation,
        statistical_evaluation,
        robustness_evaluation,
        contradiction_evaluation,
        evidence_strength_evaluation,
        hypothesis_decision,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_evidence_strength(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert experiment.status == ExperimentStatus.COMPLETED
    assert result.experiment_id == experiment.id

    assert evaluation.is_valid is True

    assert statistical_evaluation.is_evaluated is True
    assert statistical_evaluation.is_significant is True
    assert statistical_evaluation.p_value is not None
    assert statistical_evaluation.effect_size is not None

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True

    assert contradiction_evaluation.is_evaluated is True
    assert contradiction_evaluation.has_contradiction is False

    assert evidence_strength_evaluation.is_evaluated is True
    assert evidence_strength_evaluation.level == "very_strong"
    assert evidence_strength_evaluation.score > 0.90

    assert evidence_strength_evaluation.result_is_valid is True
    assert (
        evidence_strength_evaluation.statistically_significant
        is True
    )
    assert evidence_strength_evaluation.robust is True
    assert (
        evidence_strength_evaluation.has_contradiction
        is False
    )

    assert evidence_strength_evaluation.component_scores[
        "validation"
    ] == pytest.approx(1.0)

    assert evidence_strength_evaluation.component_scores[
        "statistical_significance"
    ] == pytest.approx(1.0)

    assert evidence_strength_evaluation.component_scores[
        "robustness"
    ] == pytest.approx(1.0)

    assert evidence_strength_evaluation.component_scores[
        "contradiction_absence"
    ] == pytest.approx(1.0)

    assert evidence_strength_evaluation.component_scores[
        "p_value_strength"
    ] > 0.0

    assert evidence_strength_evaluation.component_scores[
        "effect_size_strength"
    ] == pytest.approx(1.0)

    assert evidence_strength_evaluation.warnings == []

    assert hypothesis_decision.is_evaluated is True
    assert hypothesis_decision.is_supported is True
    assert hypothesis_decision.confidence == pytest.approx(1.0)

    assert evidence.data == result.metrics

    assert analysis.findings["evidence_strength_evaluated"] is True
    assert analysis.findings["evidence_strength_level"] == "very_strong"
    assert analysis.findings["evidence_strength_score"] > 0.90

    assert analysis.findings[
        "evidence_strength_component_scores"
    ] == pytest.approx(
        evidence_strength_evaluation.component_scores
    )

    assert analysis.findings["evidence_strength_warnings"] == []

    assert analysis.findings["hypothesis_decision_evaluated"] is True
    assert analysis.findings["hypothesis_supported"] is True

    assert conclusion.supported is True
    assert conclusion.confidence == pytest.approx(1.0)
    assert conclusion.is_provisional is False

    assert knowledge.confidence == pytest.approx(1.0)
    assert knowledge.is_provisional is False
    assert knowledge.statement == conclusion.statement