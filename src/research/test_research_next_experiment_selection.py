import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_selects_next_experiment_action() -> None:
    question = Question(
        title="Next experiment research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Next experiment selection experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 1.0,
                "total_trades": 4,
            },
            observations={
                "profit_percent": [1.0, -0.5, 2.0, 1.5],
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
        next_experiment_selection,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_next_experiment_selection(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert experiment.status == ExperimentStatus.COMPLETED
    assert result.experiment_id == experiment.id

    assert evaluation.is_valid is True

    assert statistical_evaluation.is_evaluated is True
    assert statistical_evaluation.sample_size == 4
    assert statistical_evaluation.is_significant is False

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True

    assert contradiction_evaluation.is_evaluated is True
    assert contradiction_evaluation.has_contradiction is False

    assert evidence_strength_evaluation.is_evaluated is True
    assert evidence_strength_evaluation.score > 0.0

    assert hypothesis_decision.is_evaluated is True
    assert hypothesis_decision.is_supported is False
    assert hypothesis_decision.confidence == pytest.approx(0.75)

    assert next_experiment_selection.is_selected is True
    assert next_experiment_selection.action == "increase_sample_size"
    assert next_experiment_selection.priority == "high"
    assert next_experiment_selection.target_requirement == "sample_size"

    assert next_experiment_selection.evidence_strength_score == pytest.approx(
        evidence_strength_evaluation.score
    )
    assert (
        next_experiment_selection.evidence_strength_level
        == evidence_strength_evaluation.level
    )

    assert next_experiment_selection.failed_requirements == [
        "Result is not statistically significant"
    ]

    assert len(next_experiment_selection.recommendations) == 3
    assert next_experiment_selection.warnings == []

    assert evidence.data == result.metrics

    assert analysis.findings["next_experiment_selected"] is True
    assert (
        analysis.findings["next_experiment_action"]
        == "increase_sample_size"
    )
    assert analysis.findings["next_experiment_priority"] == "high"
    assert (
        analysis.findings["next_experiment_target_requirement"]
        == "sample_size"
    )

    assert analysis.findings[
        "next_experiment_reason"
    ] == next_experiment_selection.reason

    assert analysis.findings[
        "next_experiment_recommendations"
    ] == next_experiment_selection.recommendations

    assert analysis.findings["next_experiment_warnings"] == []

    assert conclusion.supported is False
    assert conclusion.is_provisional is False
    assert conclusion.confidence == pytest.approx(0.75)

    assert knowledge.is_provisional is False
    assert knowledge.confidence == pytest.approx(0.75)
    assert knowledge.statement == conclusion.statement