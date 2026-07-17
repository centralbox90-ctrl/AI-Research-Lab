from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_many_experiments_with_evaluation() -> None:
    question = Question(
        title="Series evaluation research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment results are technically valid",
    )

    experiments = [
        Experiment(
            hypothesis_id=hypothesis.id,
            title="Experiment 1",
            parameters={"period": 10},
        ),
        Experiment(
            hypothesis_id=hypothesis.id,
            title="Experiment 2",
            parameters={"period": 14},
        ),
        Experiment(
            hypothesis_id=hypothesis.id,
            title="Experiment 3",
            parameters={"period": 20},
        ),
    ]

    def execute(experiment: Experiment) -> ExperimentResult:
        period = int(experiment.parameters["period"])
        profit = float(period - 12)

        return ExperimentResult(
            experiment_id=experiment.id,
            success=profit > 0,
            metrics={"net_profit": profit},
            conclusion="Experiment completed",
        )

    cycles = ResearchEngine().run_many_with_evaluation(
        question=question,
        hypothesis=hypothesis,
        experiments=experiments,
        executor=execute,
    )

    assert len(cycles) == 3

    assert all(
        experiment.status == ExperimentStatus.COMPLETED
        for experiment in experiments
    )

    results = [cycle[0] for cycle in cycles]
    evaluations = [cycle[1] for cycle in cycles]

    assert results[0].metrics["net_profit"] == -2.0
    assert results[1].metrics["net_profit"] == 2.0
    assert results[2].metrics["net_profit"] == 8.0

    assert all(
        evaluation.is_valid is True
        for evaluation in evaluations
    )

    assert all(
        evaluation.evidence_strength == 0.0
        for evaluation in evaluations
    )

    assert all(
        evaluation.warnings == []
        for evaluation in evaluations
    )