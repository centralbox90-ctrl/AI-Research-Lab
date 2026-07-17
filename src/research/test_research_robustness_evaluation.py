import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_cycle_with_robustness_evaluation() -> None:
    question = Question(
        title="Robustness research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Robustness experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 4.0,
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
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_robustness_evaluation(
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
    assert statistical_evaluation.mean == pytest.approx(1.0)
    assert statistical_evaluation.is_significant is False

    assert robustness_evaluation.is_evaluated is True
    assert robustness_evaluation.is_robust is True
    assert robustness_evaluation.sample_size == 4

    assert (
        robustness_evaluation.positive_observation_ratio
        == pytest.approx(0.75)
    )
    assert (
        robustness_evaluation.negative_observation_ratio
        == pytest.approx(0.25)
    )
    assert (
        robustness_evaluation.zero_observation_ratio
        == pytest.approx(0.0)
    )

    assert robustness_evaluation.first_half_mean == pytest.approx(
        0.25
    )
    assert robustness_evaluation.second_half_mean == pytest.approx(
        1.75
    )
    assert robustness_evaluation.mean_shift == pytest.approx(1.5)
    assert robustness_evaluation.direction_consistent is True

    assert evidence.data == result.metrics

    assert analysis.findings["statistics_evaluated"] is True
    assert analysis.findings["robustness_evaluated"] is True

    assert analysis.findings["statistically_significant"] is False
    assert analysis.findings["is_robust"] is True

    assert analysis.findings["robustness_sample_size"] == 4

    assert analysis.findings[
        "positive_observation_ratio"
    ] == pytest.approx(0.75)

    assert analysis.findings[
        "negative_observation_ratio"
    ] == pytest.approx(0.25)

    assert analysis.findings[
        "zero_observation_ratio"
    ] == pytest.approx(0.0)

    assert analysis.findings["first_half_mean"] == pytest.approx(
        0.25
    )
    assert analysis.findings["second_half_mean"] == pytest.approx(
        1.75
    )
    assert analysis.findings["mean_shift"] == pytest.approx(1.5)
    assert analysis.findings["direction_consistent"] is True

    assert conclusion.supported is False
    assert conclusion.confidence == 0.0
    assert conclusion.is_provisional is True
    assert (
        conclusion.basis
        == "Inferential statistics and robustness diagnostics"
    )

    assert knowledge.confidence == 0.0
    assert knowledge.is_provisional is True
    assert (
        knowledge.basis
        == "Inferential statistics and robustness diagnostics"
    )