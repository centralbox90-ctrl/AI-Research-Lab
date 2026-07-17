from src.research.analysis import Analysis
from src.research.conclusion import Conclusion
from src.research.evidence import Evidence
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.experiment_runner import ExperimentRunner
from src.research.hypothesis import Hypothesis
from src.research.knowledge import Knowledge
from src.research.question import Question
from src.research.research_plan import ResearchPlan
from src.research.research_types import ExperimentStatus


def test_research_pipeline() -> None:
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

    plan = ResearchPlan(
        question_id=question.id,
        title="Test plan",
    )
    plan.add_hypothesis(hypothesis.id)
    plan.add_experiment(experiment.id)

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={"profit": 10.0},
            conclusion="Hypothesis supported",
        )

    result = ExperimentRunner().run(experiment, execute)

    evidence = Evidence(
        experiment_id=experiment.id,
        title="Experiment metrics",
        data=result.metrics,
        source="ExperimentRunner",
    )

    analysis = Analysis(
        experiment_id=experiment.id,
        title="Experiment analysis",
        findings={
            "profitable": result.metrics["profit"] > 0,
        },
        interpretation="Positive experiment result",
    )
    analysis.add_evidence(evidence.id)

    conclusion = Conclusion(
        analysis_id=analysis.id,
        hypothesis_id=hypothesis.id,
        title="Final conclusion",
        statement=result.conclusion,
        supported=result.success,
        confidence=0.8,
    )

    knowledge = Knowledge(
        question_id=question.id,
        hypothesis_id=hypothesis.id,
        experiment_id=experiment.id,
        title="Test knowledge",
        statement=conclusion.statement,
        confidence=conclusion.confidence,
    )

    assert hypothesis.question_id == question.id
    assert experiment.hypothesis_id == hypothesis.id
    assert hypothesis.id in plan.hypothesis_ids
    assert experiment.id in plan.experiment_ids

    assert experiment.status == ExperimentStatus.COMPLETED
    assert result.experiment_id == experiment.id
    assert result.success is True

    assert evidence.experiment_id == experiment.id
    assert evidence.data == result.metrics

    assert evidence.id in analysis.evidence_ids
    assert analysis.findings["profitable"] is True

    assert conclusion.analysis_id == analysis.id
    assert conclusion.hypothesis_id == hypothesis.id
    assert conclusion.supported is True

    assert knowledge.statement == conclusion.statement
    assert knowledge.confidence == conclusion.confidence