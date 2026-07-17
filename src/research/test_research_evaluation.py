from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_cycle_with_evaluation() -> None:
    question = Question(
        title="Evaluation research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment result is valid",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Evaluation experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 8.0,
                "win_rate": 61.0,
            },
            conclusion="Experiment completed successfully",
        )

    (
        result,
        evaluation,
        evidence,
        analysis,
        conclusion,
        knowledge,
    ) = ResearchEngine().run_with_evaluation(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert experiment.status == ExperimentStatus.COMPLETED

    assert result.experiment_id == experiment.id

    assert evaluation.experiment_id == experiment.id
    assert evaluation.is_valid is True
    assert evaluation.evidence_strength == 0.0
    assert evaluation.warnings == []

    assert evidence.experiment_id == experiment.id
    assert evidence.data == result.metrics

    assert analysis.findings["success"] is True
    assert analysis.findings["result_is_valid"] is True
    assert analysis.findings["evidence_strength"] == 0.0
    assert analysis.findings["evaluation_warnings"] == []

    assert conclusion.hypothesis_id == hypothesis.id
    assert knowledge.experiment_id == experiment.id
    assert conclusion.supported is False
    assert conclusion.confidence == 0.0
    assert conclusion.is_provisional is True
    assert conclusion.basis == "Basic result validation only"

    assert knowledge.confidence == 0.0
    assert knowledge.is_provisional is True
    assert knowledge.basis == "Basic result validation only"
    assert knowledge.confidence == 0.0