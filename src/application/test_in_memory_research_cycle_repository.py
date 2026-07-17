from src.application import InMemoryResearchCycleRepository
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
    ResearchEngine,
)


def test_in_memory_repository_saves_and_returns_completed_cycle() -> None:
    question = Question(
        title="Can a completed research cycle be stored?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="A completed research cycle can be stored in memory",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="In-memory repository experiment",
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
                "profit_percent": [
                    1.8,
                    2.0,
                    2.1,
                    1.9,
                    2.2,
                ],
            },
            conclusion="A stable positive effect was observed.",
        )

    cycle = ResearchEngine().run_with_next_experiment_selection(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    repository = InMemoryResearchCycleRepository()

    repository.save(cycle)

    stored_cycle = repository.get(cycle.result.id)

    assert stored_cycle is cycle
    assert stored_cycle.result is cycle.result
    assert stored_cycle.analysis is cycle.analysis
    assert stored_cycle.hypothesis_decision.is_supported is True


def test_in_memory_repository_returns_none_for_unknown_result() -> None:
    repository = InMemoryResearchCycleRepository()

    assert repository.get("unknown-result-id") is None