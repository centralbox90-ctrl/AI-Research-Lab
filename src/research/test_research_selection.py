from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_many_and_selects_best_experiment() -> None:
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

    cycles, best = ResearchEngine().run_many_and_select_best(
        question=question,
        hypothesis=hypothesis,
        experiments=experiments,
        executor=execute,
        metric="net_profit",
    )

    assert len(cycles) == 3

    assert all(
        experiment.status == ExperimentStatus.COMPLETED
        for experiment in experiments
    )

    assert best.experiment.parameters["period"] == 20
    assert best.score == 8.0
    assert best.result.metrics["net_profit"] == 8.0
    assert best.result.success is True