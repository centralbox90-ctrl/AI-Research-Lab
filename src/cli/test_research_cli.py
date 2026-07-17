from io import StringIO

from src.application import (
    GetSerializedResearchCycle,
    InMemoryResearchCycleRepository,
    RunResearchCycle,
)
from src.cli import GetResearchCycleCommand, ResearchCli
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)


def build_cli_with_saved_cycle() -> tuple[ResearchCli, str]:
    question = Question(
        title="Can CLI arguments retrieve a saved research cycle?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="CLI argument parsing delegates to the application layer",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="CLI argument parsing experiment",
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

    return ResearchCli(command), cycle.result.id


def test_research_cli_prints_saved_cycle_json() -> None:
    cli, result_id = build_cli_with_saved_cycle()

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-research-cycle",
            result_id,
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert result_id in stdout.getvalue()
    assert '"hypothesis_decision"' in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_research_cli_supports_compact_json() -> None:
    cli, result_id = build_cli_with_saved_cycle()

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-research-cycle",
            result_id,
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    rendered = stdout.getvalue().rstrip("\n")

    assert exit_code == 0
    assert "\n" not in rendered
    assert result_id in rendered
    assert stderr.getvalue() == ""


def test_research_cli_reports_missing_cycle() -> None:
    repository = InMemoryResearchCycleRepository()

    command = GetResearchCycleCommand(
        get_serialized_research_cycle=GetSerializedResearchCycle(
            repository=repository,
        ),
    )

    cli = ResearchCli(command)

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "get-research-cycle",
            "unknown-result-id",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == "Research cycle not found: unknown-result-id\n"
    )