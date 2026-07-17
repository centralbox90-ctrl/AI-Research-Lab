from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_full_cycle() -> None:
    question = Question(
        title="Test question",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Test hypothesis",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Test experiment",
        parameters={"period": 14},
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={"profit": 10.0},
            conclusion="Hypothesis supported",
        )

    result, evidence, analysis, conclusion, knowledge = (
        ResearchEngine().run(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=execute,
        )
    )

    assert experiment.status == ExperimentStatus.COMPLETED

    assert result.experiment_id == experiment.id
    assert result.success is True

    assert evidence.experiment_id == experiment.id
    assert evidence.data == result.metrics

    assert evidence.id in analysis.evidence_ids
    assert analysis.experiment_id == experiment.id

    assert conclusion.analysis_id == analysis.id
    assert conclusion.hypothesis_id == hypothesis.id
    assert conclusion.supported is True

    assert knowledge.question_id == question.id
    assert knowledge.hypothesis_id == hypothesis.id
    assert knowledge.experiment_id == experiment.id
    assert knowledge.statement == conclusion.statement