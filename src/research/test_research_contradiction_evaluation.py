import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_cycle_with_contradiction_evaluation() -> None:
    question = Question(
        title="Contradiction research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Contradiction experiment",
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
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_contradiction_evaluation(
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
    assert statistical_evaluation.sample_size == 5
    assert statistical_evaluation.mean == pytest.approx(2.0)
    assert statistical_evaluation.p_value is not None
    assert (
        statistical_evaluation.p_value
        < statistical_evaluation.significance_level
    )

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True
    assert robustness_evaluation.sample_size == 5
    assert robustness_evaluation.direction_consistent is True

    assert contradiction_evaluation.is_evaluated is True
    assert contradiction_evaluation.has_contradiction is False

    assert contradiction_evaluation.observed_direction == "positive"
    assert contradiction_evaluation.statistically_significant is True
    assert contradiction_evaluation.robust is True

    assert (
        contradiction_evaluation.significance_robustness_conflict
        is False
    )
    assert (
        contradiction_evaluation.direction_robustness_conflict
        is False
    )
    assert contradiction_evaluation.contradiction_count == 0
    assert contradiction_evaluation.warnings == []

    assert evidence.data == result.metrics

    assert analysis.findings["statistics_evaluated"] is True
    assert analysis.findings["statistically_significant"] is True

    assert analysis.findings["robustness_evaluated"] is True
    assert analysis.findings["is_robust"] is True

    assert analysis.findings["contradictions_evaluated"] is True
    assert analysis.findings["has_contradiction"] is False
    assert analysis.findings["observed_direction"] == "positive"

    assert (
        analysis.findings["contradiction_statistically_significant"]
        is True
    )
    assert analysis.findings["contradiction_robust"] is True

    assert (
        analysis.findings["significance_robustness_conflict"]
        is False
    )
    assert (
        analysis.findings["direction_robustness_conflict"]
        is False
    )
    assert analysis.findings["contradiction_count"] == 0
    assert analysis.findings["contradiction_warnings"] == []

    assert conclusion.supported is False
    assert conclusion.confidence == 0.0
    assert conclusion.is_provisional is True
    assert (
        conclusion.basis
        == (
            "Inferential statistics, robustness and "
            "contradiction evaluation"
        )
    )

    assert knowledge.confidence == 0.0
    assert knowledge.is_provisional is True
    assert (
        knowledge.basis
        == (
            "Inferential statistics, robustness and "
            "contradiction evaluation"
        )
    )