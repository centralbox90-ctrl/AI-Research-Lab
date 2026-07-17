from src.research.experiment import Experiment
from src.research.experiment_comparator import ExperimentComparator
from src.research.experiment_result import ExperimentResult


def test_experiment_comparator_ranks_and_selects_best() -> None:
    experiments = [
        Experiment(
            title="Experiment 1",
            parameters={"period": 10},
        ),
        Experiment(
            title="Experiment 2",
            parameters={"period": 14},
        ),
        Experiment(
            title="Experiment 3",
            parameters={"period": 20},
        ),
    ]

    results = [
        ExperimentResult(
            experiment_id=experiments[0].id,
            success=False,
            metrics={"net_profit": -2.0},
        ),
        ExperimentResult(
            experiment_id=experiments[1].id,
            success=True,
            metrics={"net_profit": 2.0},
        ),
        ExperimentResult(
            experiment_id=experiments[2].id,
            success=True,
            metrics={"net_profit": 8.0},
        ),
    ]

    comparator = ExperimentComparator()

    ranked = comparator.rank(
        experiments=experiments,
        results=results,
        metric="net_profit",
    )

    best = comparator.best(
        experiments=experiments,
        results=results,
        metric="net_profit",
    )

    assert len(ranked) == 3

    assert ranked[0].experiment.id == experiments[2].id
    assert ranked[0].score == 8.0

    assert ranked[1].experiment.id == experiments[1].id
    assert ranked[1].score == 2.0

    assert ranked[2].experiment.id == experiments[0].id
    assert ranked[2].score == -2.0

    assert best.experiment.id == experiments[2].id
    assert best.result.experiment_id == experiments[2].id
    assert best.score == 8.0