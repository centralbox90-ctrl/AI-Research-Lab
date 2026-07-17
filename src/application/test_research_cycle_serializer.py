from src.application import ResearchCycleSerializer
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
    ResearchEngine,
)


def test_research_cycle_serializer_uses_named_cycle_fields() -> None:
    question = Question(
        title="Can a completed research cycle be serialized?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Completed cycles can be serialized for adapters",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Research cycle serialization experiment",
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

    serializer = ResearchCycleSerializer()

    serialized = serializer.serialize(cycle)

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

    assert serialized["analysis"]["findings"][
        "hypothesis_supported"
    ] is True

    assert serialized["conclusion"]["supported"] is True
    assert serialized["knowledge"]["is_provisional"] is False

    assert isinstance(
        serialized["result"]["created_at"],
        str,
    )

    result, *_ = cycle
    assert result is cycle.result
    assert len(cycle) == 12