from io import StringIO

from src.cli.research_cli import ResearchCli


class FakeGetResearchCycleCommand:
    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        return None


class FakeCompareResearchArtifactsCommand:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int | None]] = []

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
        *,
        indent: int | None = 2,
    ) -> str:
        self.calls.append(
            (
                artifact_a_result_id,
                artifact_b_result_id,
                indent,
            )
        )

        return (
            '{"artifact_a_id": "artifact-001", '
            '"artifact_b_id": "artifact-002"}'
        )


def test_research_cli_runs_compare_research_artifacts():

    compare_command = FakeCompareResearchArtifactsCommand()

    cli = ResearchCli(
        get_research_cycle_command=(
            FakeGetResearchCycleCommand()
        ),
        compare_research_artifacts_command=(
            compare_command
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "compare-research-artifacts",
            "result-001",
            "result-002",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0

    assert compare_command.calls == [
        (
            "result-001",
            "result-002",
            2,
        )
    ]

    assert (
        stdout.getvalue()
        == (
            '{"artifact_a_id": "artifact-001", '
            '"artifact_b_id": "artifact-002"}\n'
        )
    )

    assert stderr.getvalue() == ""


def test_research_cli_runs_compact_artifact_comparison():

    compare_command = FakeCompareResearchArtifactsCommand()

    cli = ResearchCli(
        get_research_cycle_command=(
            FakeGetResearchCycleCommand()
        ),
        compare_research_artifacts_command=(
            compare_command
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "compare-research-artifacts",
            "result-001",
            "result-002",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0

    assert compare_command.calls == [
        (
            "result-001",
            "result-002",
            None,
        )
    ]

    assert stderr.getvalue() == ""


def test_research_cli_reports_compare_command_not_configured():

    cli = ResearchCli(
        get_research_cycle_command=(
            FakeGetResearchCycleCommand()
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "compare-research-artifacts",
            "result-001",
            "result-002",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2

    assert stdout.getvalue() == ""

    assert (
        stderr.getvalue()
        == (
            "Compare research artifacts command "
            "is not configured.\n"
        )
    )