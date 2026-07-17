import json

from src.application import (
    GetSerializedResearchCycle,
    InMemoryResearchCycleRepository,
    RunResearchCycle,
)
from src.cli import GetResearchCycleCommand
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)


def test_get_research_cycle_command_returns_saved_cycle_as_json() -> None:
    question = Question(
        title="Can the CLI retrieve a saved research cycle?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="The CLI can present a saved cycle as JSON",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="CLI research cycle retrieval experiment",
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

    command = GetResearchCycleCommand(
        get_serialized_research_cycle=get_serialized_use_case,
    )

    rendered = command.execute(cycle.result.id)

    assert rendered is not None

    parsed = json.loads(rendered)

    assert parsed["result"]["id"] == cycle.result.id
    assert parsed["result"]["success"] is True

    assert (
        parsed["evidence_strength_evaluation"]["level"]
        == "very_strong"
    )

    assert parsed["hypothesis_decision"]["is_supported"] is True

    assert (
        parsed["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )


def test_get_research_cycle_command_returns_none_when_cycle_missing() -> None:
    repository = InMemoryResearchCycleRepository()

    get_serialized_use_case = GetSerializedResearchCycle(
        repository=repository,
    )

    command = GetResearchCycleCommand(
        get_serialized_research_cycle=get_serialized_use_case,
    )

    assert command.execute("unknown-result-id") is None


def test_get_research_cycle_command_supports_compact_json() -> None:
    question = Question(
        title="Can the CLI return compact JSON?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="The CLI supports compact cycle output",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Compact CLI output experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
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

    cycle = RunResearchCycle(
        repository=repository,
    ).execute(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    command = GetResearchCycleCommand(
        get_serialized_research_cycle=GetSerializedResearchCycle(
            repository=repository,
        ),
    )

    rendered = command.execute(
        cycle.result.id,
        indent=None,
    )

    assert rendered is not None
    assert "\n" not in rendered
    assert json.loads(rendered)["result"]["id"] == cycle.result.id