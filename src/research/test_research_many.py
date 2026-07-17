from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_many_experiments() -> None:
    question = Question(
        title="Parameter research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="One parameter set is profitable",
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
            conclusion=(
                "Hypothesis supported"
                if profit > 0
                else "Hypothesis not supported"
            ),
        )

    cycles = ResearchEngine().run_many(
        question=question,
        hypothesis=hypothesis,
        experiments=experiments,
        executor=execute,
    )

    assert len(cycles) == 3

    results = [cycle[0] for cycle in cycles]

    assert all(
        experiment.status == ExperimentStatus.COMPLETED
        for experiment in experiments
    )

    assert results[0].metrics["net_profit"] == -2.0
    assert results[0].success is False

    assert results[1].metrics["net_profit"] == 2.0
    assert results[1].success is True

    assert results[2].metrics["net_profit"] == 8.0
    assert results[2].success is True