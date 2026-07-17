from src.application import (
    GetSerializedResearchCycle,
    InMemoryResearchCycleRepository,
    RunResearchCycle,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)


def test_get_serialized_research_cycle_returns_adapter_safe_data() -> None:
    question = Question(
        title="Can a saved cycle be returned as serialized data?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Saved cycles can be prepared for external adapters",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Serialized cycle retrieval experiment",
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

    get_serialized_use_case = GetSerializedResearchCycle(
        repository=repository,
    )

    serialized = get_serialized_use_case.execute(cycle.result.id)

    assert serialized is not None
    assert serialized["result"]["id"] == cycle.result.id
    assert serialized["result"]["success"] is True

    assert (
        serialized["evidence_strength_evaluation"]["level"]
        == "very_strong"
    )

    assert (
        serialized["hypothesis_decision"]["is_supported"]
        is True
    )

    assert (
        serialized["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )

    assert serialized["conclusion"]["supported"] is True
    assert serialized["knowledge"]["is_provisional"] is False


def test_get_serialized_research_cycle_returns_none_when_missing() -> None:
    repository = InMemoryResearchCycleRepository()

    use_case = GetSerializedResearchCycle(
        repository=repository,
    )

    assert use_case.execute("unknown-result-id") is None