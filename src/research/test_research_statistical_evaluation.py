import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_cycle_with_statistical_evaluation() -> None:
    question = Question(
        title="Statistical research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Statistical experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 3.0,
                "total_trades": 3,
            },
            observations={
                "profit_percent": [1.5, -0.5, 2.0],
            },
            conclusion="Experiment completed successfully",
        )

    (
        result,
        evaluation,
        statistical_evaluation,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_statistical_evaluation(
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
    assert statistical_evaluation.sample_size == 3
    assert statistical_evaluation.mean == pytest.approx(1.0)
    assert statistical_evaluation.standard_deviation == pytest.approx(
        1.3228756555322954
    )
    assert statistical_evaluation.standard_error == pytest.approx(
        0.7637626158259734
    )
    assert statistical_evaluation.confidence_interval_lower == pytest.approx(
        -0.49697472701890777
    )
    assert statistical_evaluation.confidence_interval_upper == pytest.approx(
        2.496974727018908
    )
    assert statistical_evaluation.confidence_level == pytest.approx(0.95)

    assert statistical_evaluation.null_mean == 0.0
    assert statistical_evaluation.alternative == "two-sided"
    assert statistical_evaluation.significance_level == 0.05
    assert (
        statistical_evaluation.test_method
        == "one-sample Student t-test"
    )
    assert statistical_evaluation.test_statistic == pytest.approx(
        1.3093073414159542
    )
    assert statistical_evaluation.p_value == pytest.approx(
        0.3206337795132426
    )
    assert statistical_evaluation.effect_size == pytest.approx(
        0.7559289460184544
    )

    assert evidence.data == result.metrics

    assert analysis.findings["statistics_evaluated"] is True
    assert analysis.findings["statistically_significant"] is False
    assert analysis.findings["sample_size"] == 3
    assert analysis.findings["mean"] == pytest.approx(1.0)
    assert analysis.findings["standard_deviation"] == pytest.approx(
        1.3228756555322954
    )
    assert analysis.findings["standard_error"] == pytest.approx(
        0.7637626158259734
    )
    assert analysis.findings[
        "confidence_interval_lower"
    ] == pytest.approx(
        -0.49697472701890777
    )
    assert analysis.findings[
        "confidence_interval_upper"
    ] == pytest.approx(
        2.496974727018908
    )
    assert analysis.findings["confidence_level"] == pytest.approx(0.95)

    assert analysis.findings["null_mean"] == 0.0
    assert analysis.findings["alternative"] == "two-sided"
    assert analysis.findings["significance_level"] == 0.05
    assert (
        analysis.findings["test_method"]
        == "one-sample Student t-test"
    )
    assert analysis.findings["test_statistic"] == pytest.approx(
        1.3093073414159542
    )
    assert analysis.findings["p_value"] == pytest.approx(
        0.3206337795132426
    )
    assert analysis.findings["effect_size"] == pytest.approx(
        0.7559289460184544
    )

    assert conclusion.supported is False
    assert conclusion.confidence == 0.0
    assert conclusion.is_provisional is True
    assert conclusion.basis == "Inferential statistics only"

    assert knowledge.confidence == 0.0
    assert knowledge.is_provisional is True
    assert knowledge.basis == "Inferential statistics only"