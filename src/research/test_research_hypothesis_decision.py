import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_supports_hypothesis_after_full_evaluation() -> None:
    question = Question(
        title="Scientific decision research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Supported hypothesis experiment",
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
        hypothesis_decision,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_hypothesis_decision(
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
    assert (
        statistical_evaluation.p_value
        < statistical_evaluation.significance_level
    )

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True

    assert contradiction_evaluation.is_evaluated is True
    assert contradiction_evaluation.has_contradiction is False
    assert contradiction_evaluation.contradiction_count == 0

    assert hypothesis_decision.is_evaluated is True
    assert hypothesis_decision.is_supported is True
    assert hypothesis_decision.result_is_valid is True
    assert hypothesis_decision.statistically_significant is True
    assert hypothesis_decision.robust is True
    assert hypothesis_decision.has_contradiction is False
    assert hypothesis_decision.confidence == pytest.approx(1.0)
    assert hypothesis_decision.failed_requirements == []
    assert hypothesis_decision.warnings == []

    assert evidence.data == result.metrics

    assert analysis.findings["hypothesis_decision_evaluated"] is True
    assert analysis.findings["hypothesis_supported"] is True
    assert analysis.findings["decision_confidence"] == pytest.approx(
        1.0
    )
    assert analysis.findings["decision_failed_requirements"] == []
    assert analysis.findings["decision_warnings"] == []

    assert conclusion.supported is True
    assert conclusion.confidence == pytest.approx(1.0)
    assert conclusion.is_provisional is False
    assert (
        conclusion.statement
        == (
            "The hypothesis is supported by the completed "
            "scientific evaluation pipeline."
        )
    )
    assert (
        conclusion.basis
        == (
            "Basic validation, inferential statistics, robustness "
            "and contradiction evaluation"
        )
    )

    assert knowledge.confidence == pytest.approx(1.0)
    assert knowledge.is_provisional is False
    assert knowledge.statement == conclusion.statement
    assert knowledge.basis == conclusion.basis


def test_research_engine_rejects_hypothesis_after_full_evaluation() -> None:
    question = Question(
        title="Scientific rejection research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Rejected hypothesis experiment",
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
        hypothesis_decision,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_hypothesis_decision(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert experiment.status == ExperimentStatus.COMPLETED
    assert result.experiment_id == experiment.id

    assert evaluation.is_valid is True

    assert statistical_evaluation.is_evaluated is True
    assert statistical_evaluation.is_significant is False

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True

    assert contradiction_evaluation.is_evaluated is True
    assert contradiction_evaluation.has_contradiction is False

    assert hypothesis_decision.is_evaluated is True
    assert hypothesis_decision.is_supported is False

    assert hypothesis_decision.result_is_valid is True
    assert hypothesis_decision.statistically_significant is False
    assert hypothesis_decision.robust is True
    assert hypothesis_decision.has_contradiction is False

    assert hypothesis_decision.confidence == pytest.approx(0.75)
    assert hypothesis_decision.failed_requirements == [
        "Result is not statistically significant"
    ]
    assert hypothesis_decision.warnings == []

    assert evidence.data == result.metrics

    assert analysis.findings["hypothesis_decision_evaluated"] is True
    assert analysis.findings["hypothesis_supported"] is False
    assert analysis.findings["decision_confidence"] == pytest.approx(
        0.75
    )
    assert analysis.findings["decision_failed_requirements"] == [
        "Result is not statistically significant"
    ]
    assert analysis.findings["decision_warnings"] == []

    assert conclusion.supported is False
    assert conclusion.confidence == pytest.approx(0.75)
    assert conclusion.is_provisional is False
    assert (
        conclusion.statement
        == (
            "The hypothesis is not supported by the completed "
            "scientific evaluation pipeline."
        )
    )
    assert (
        conclusion.basis
        == (
            "Basic validation, inferential statistics, robustness "
            "and contradiction evaluation"
        )
    )

    assert knowledge.confidence == pytest.approx(0.75)
    assert knowledge.is_provisional is False
    assert knowledge.statement == conclusion.statement
    assert knowledge.basis == conclusion.basis