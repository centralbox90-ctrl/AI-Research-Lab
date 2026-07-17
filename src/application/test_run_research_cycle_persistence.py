from src.application import (
    InMemoryResearchCycleRepository,
    RunResearchCycle,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)


def test_run_research_cycle_saves_completed_cycle() -> None:
    question = Question(
        title="Can the application use case persist a research cycle?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="The application use case persists completed cycles",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Application persistence experiment",
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

    use_case = RunResearchCycle(
        repository=repository,
    )

    cycle = use_case.execute(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    stored_cycle = repository.get(cycle.result.id)

    assert stored_cycle is cycle
    assert stored_cycle.result is cycle.result
    assert stored_cycle.analysis is cycle.analysis
    assert stored_cycle.knowledge is cycle.knowledge