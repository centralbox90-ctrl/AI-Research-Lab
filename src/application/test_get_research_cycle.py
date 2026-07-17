from src.application import (
    GetResearchCycle,
    InMemoryResearchCycleRepository,
    RunResearchCycle,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)


def test_get_research_cycle_returns_saved_cycle() -> None:
    question = Question(
        title="Can a saved research cycle be retrieved?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Saved cycles can be retrieved through a use case",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Research cycle retrieval experiment",
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

    repository = InMemoryResearchCycleRepository()

    run_use_case = RunResearchCycle(
        repository=repository,
    )

    cycle = run_use_case.execute(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    get_use_case = GetResearchCycle(
        repository=repository,
    )

    stored_cycle = get_use_case.execute(cycle.result.id)

    assert stored_cycle is cycle
    assert stored_cycle.result is cycle.result
    assert stored_cycle.hypothesis_decision.is_supported is True
    assert stored_cycle.next_experiment_selection.is_selected is True


def test_get_research_cycle_returns_none_for_unknown_result() -> None:
    repository = InMemoryResearchCycleRepository()

    get_use_case = GetResearchCycle(
        repository=repository,
    )

    assert get_use_case.execute("unknown-result-id") is None